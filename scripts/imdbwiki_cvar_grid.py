# (alpha, gamma) grid for the CVaR x FedAVOT study in the INFEASIBLE IMDb-Wiki regime,
# plus a third, stability-safe combination variant ("cvar_tilt"):
#   cvar_avot : paper Algorithm 1 locally (G_i gradient scaling on theta and t),
#               transport-weighted aggregation  [the literal combination]
#   cvar_unif : paper Algorithm 1 locally, uniform mean over S  [paper-style, RAM-agnostic]
#   cvar_tilt : risk-neutral local training, but aggregation weights tilted by the CVaR
#               hinge:  w_i ∝ Y[i,j] * ((1-g)/a * 1{f_i > t} + g), renormalized to a convex
#               combination; t updated at the server. Risk-awareness reshapes WHO counts,
#               not the step size -> cannot blow up.
# All configs see identical subset draws (pre-generated per seed). Baselines (risk-neutral
# FedAVOT, FedAvg(full)) run once per seed. Divergence guard freezes a model at cap 1e12.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
import time

# ================================================================
# Config
# ================================================================
NUM_USERS = 100
K = 3
ROUNDS = 4000
LOCAL_EPOCHS = 5
SAMPLES_PER_USER = 30
LR = 0.01
SEEDS = [0, 1, 2]
NUM_SAMPLES_FOR_Q = 1_000_000
IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000
TAIL = 500

ALPHAS = [0.1, 0.2, 0.3, 0.5]
GAMMAS = [0.1, 0.3]
ETA_T = 0.05
T0 = 0.0
CAP = 1e12
VARIANTS = ('cvar_avot', 'cvar_unif', 'cvar_tilt')

# ================================================================
# Transport (as in the other IMDb-Wiki scripts)
# ================================================================
def build_mask(n, subsets):
    M = np.zeros((n, len(subsets)), dtype=bool)
    for j, s in enumerate(subsets):
        for i in s:
            M[i-1, j] = True
    return M

def ipfp_masked(p, q, M, tol, max_iter):
    Y = np.zeros_like(M, dtype=float)
    for j in range(M.shape[1]):
        rows = np.where(M[:, j])[0]
        if rows.size:
            Y[rows, j] = q[j] / rows.size
    row_err = np.inf
    for _ in range(max_iter):
        Y *= (p / np.maximum(Y.sum(axis=1), 1e-12))[:, None]
        Y *= (q / np.maximum(Y.sum(axis=0), 1e-12))[None, :]
        row_err = np.max(np.abs(Y.sum(axis=1) - p))
        if row_err < tol:
            break
    return Y, row_err

def solve_T(p, q, subsets):
    M = build_mask(len(p), subsets)
    Y, row_err = ipfp_masked(p, q, M, IPFP_TOL, IPFP_MAX_ITERS)
    print(f"IPFP row_err = {row_err:.2e}")
    T = np.zeros_like(Y)
    pos = q > 0
    T[:, pos] = Y[:, pos] / q[pos]
    T[~M] = 0
    s = T.sum(axis=0, keepdims=True); s[s == 0] = 1.0
    T /= s
    return T

def column_users_and_weights(T, subsets, j):
    rows = np.array([i-1 for i in subsets[j]])
    w = T[rows, j]
    ss = w.sum()
    return rows, (w/ss if ss > 0 else np.full(len(rows), 1.0/len(rows)))

# ================================================================
# Learners
# ================================================================
def batched_local_train(Xs, ys, w, epochs):
    W = np.repeat(w[None, :], Xs.shape[0], axis=0)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        grad = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * grad
    return W

def batched_local_train_cvar(Xs, ys, w, t, epochs, a, g):
    m = Xs.shape[0]
    W = np.repeat(w[None, :], m, axis=0)
    Tv = np.full(m, t)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        f = (resid ** 2).mean(axis=1)
        active = (f > Tv).astype(float)
        coef = (1.0 - g) / a * active + g
        grad_w = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * coef[:, None] * grad_w
        Tv = Tv - ETA_T * (1.0 - g) * (1.0 - active / a)
    return W, Tv

def local_losses(Xs, ys, w):
    resid = np.einsum('msd,d->ms', Xs, w) - ys
    return (resid ** 2).mean(axis=1)

def global_loss_vec(w, X_all, y_all, p):
    resid = np.einsum('nsd,d->ns', X_all, w) - y_all
    return p @ (resid ** 2).mean(axis=1)

def group_loss(w, X_all, y_all, p, mask):
    resid = np.einsum('nsd,d->ns', X_all[mask], w) - y_all[mask]
    pm = p[mask]
    return pm @ (resid ** 2).mean(axis=1) / pm.sum()

# ================================================================
# Distributions / data (mirrored cubic = infeasible)
# ================================================================
def make_distributions(N):
    idx = np.arange(1, N+1)
    return (idx[::-1]**3 / (idx**3).sum(), (idx**3).astype(float) / (idx**3).sum())

def estimate_q(subsets, r, N, K, samples, rng):
    lookup = {s: i for i, s in enumerate(subsets)}
    counts = np.zeros(len(subsets))
    logr = np.log(r)
    done = 0
    while done < samples:
        b = min(50_000, samples - done)
        gmb = rng.gumbel(size=(b, N)) + logr[None, :]
        tk = np.argpartition(-gmb, K, axis=1)[:, :K]
        tk.sort(axis=1)
        for row in tk + 1:
            counts[lookup[tuple(row.tolist())]] += 1
        done += b
    return counts / counts.sum()

def inclusion_probs(r, N, K, samples, rng):
    gmb = rng.gumbel(size=(samples, N)) + np.log(r)[None, :]
    tk = np.argpartition(-gmb, K, axis=1)[:, :K]
    incl = np.zeros(N)
    np.add.at(incl, tk.ravel(), 1)
    return incl / samples

df = pd.read_csv("data/imdb_wiki.csv")
df = df[df["split"] == "train"]
df["client_id"] = df["path"].str.extract(r"(nm\d+)")
groups = [g for _, g in df.groupby("client_id") if len(g) >= SAMPLES_PER_USER]
groups = groups[:NUM_USERS]
EMB = np.load("data/imdb_embeddings.npy", allow_pickle=True).item()
DIM = next(iter(EMB.values())).shape[0]

p, r = make_distributions(NUM_USERS)
p = p / p.sum(); r = r / r.sum()
pi = inclusion_probs(r, NUM_USERS, K, 500_000, np.random.RandomState(0))
infeas_mask = p > pi
print(f"infeasible users: {infeas_mask.sum()}/{NUM_USERS}, p-mass {p[infeas_mask].sum()*100:.1f}%")

subsets = list(combinations(range(1, NUM_USERS+1), K))
q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, np.random.RandomState(0))
q = (q + 1e-12) / q.sum()
T = solve_T(p, q, subsets)
q_cum = np.cumsum(q)

# per-seed data and identical draw sequences for every config
seed_data, seed_draws = {}, {}
for seed in SEEDS:
    rng = np.random.RandomState(seed)
    X_full = np.concatenate([np.stack([EMB[pth] for pth in g["path"].values[:SAMPLES_PER_USER]])
                             for g in groups])
    y_full = np.concatenate([g["age"].values[:SAMPLES_PER_USER] for g in groups]).astype(float)
    y_full -= y_full.mean()
    seed_data[seed] = (X_full.reshape(NUM_USERS, SAMPLES_PER_USER, DIM),
                       y_full.reshape(NUM_USERS, SAMPLES_PER_USER))
    seed_draws[seed] = np.searchsorted(q_cum, rng.rand(ROUNDS))

# ================================================================
# Baselines (risk-neutral FedAVOT + FedAvg(full)), once per seed
# ================================================================
base_curves = {'avot': [], 'full': []}
for seed in SEEDS:
    X_all, y_all = seed_data[seed]
    w_a = np.zeros(DIM); w_f = np.zeros(DIM)
    La, Lf = [], []
    for j in seed_draws[seed]:
        users, weights = column_users_and_weights(T, subsets, j)
        w_a = weights @ batched_local_train(X_all[users], y_all[users], w_a, LOCAL_EPOCHS)
        w_f = p @ batched_local_train(X_all, y_all, w_f, LOCAL_EPOCHS)
        La.append(global_loss_vec(w_a, X_all, y_all, p))
        Lf.append(global_loss_vec(w_f, X_all, y_all, p))
    base_curves['avot'].append(La); base_curves['full'].append(Lf)
print(f"baselines: avot={np.mean([np.mean(c[-TAIL:]) for c in base_curves['avot']]):.2f} "
      f"full={np.mean([np.mean(c[-TAIL:]) for c in base_curves['full']]):.2f}")

# ================================================================
# Grid
# ================================================================
results = {}          # (a, g) -> {variant: {'overall': [...], 'inf': [...], 'feas': [...]}}
best_curves = {}      # (a, g, variant) -> per-seed curves (kept for all, small enough)
for a in ALPHAS:
    for g in GAMMAS:
        res = {v: {'overall': [], 'inf': [], 'feas': []} for v in VARIANTS}
        t0 = time.time()
        for seed in SEEDS:
            X_all, y_all = seed_data[seed]
            w = {v: np.zeros(DIM) for v in VARIANTS}
            tt = {v: T0 for v in VARIANTS}
            dead = {v: False for v in VARIANTS}
            L = {v: [] for v in VARIANTS}
            for j in seed_draws[seed]:
                users, weights = column_users_and_weights(T, subsets, j)
                Xu, yu = X_all[users], y_all[users]

                # literal combination: CVaR local training, transport aggregation
                if not dead['cvar_avot']:
                    W_, Tv_ = batched_local_train_cvar(Xu, yu, w['cvar_avot'], tt['cvar_avot'],
                                                       LOCAL_EPOCHS, a, g)
                    w['cvar_avot'] = weights @ W_; tt['cvar_avot'] = weights @ Tv_

                # paper-style: CVaR local training, uniform aggregation
                if not dead['cvar_unif']:
                    W_, Tv_ = batched_local_train_cvar(Xu, yu, w['cvar_unif'], tt['cvar_unif'],
                                                       LOCAL_EPOCHS, a, g)
                    w['cvar_unif'] = W_.mean(axis=0); tt['cvar_unif'] = Tv_.mean()

                # tilted combination: risk-neutral local training, hinge-tilted transport
                # weights (renormalized -> convex), server-side t update
                if not dead['cvar_tilt']:
                    f = local_losses(Xu, yu, w['cvar_tilt'])
                    active = (f > tt['cvar_tilt']).astype(float)
                    tilt = weights * ((1.0 - g) / a * active + g)
                    tilt = tilt / tilt.sum() if tilt.sum() > 0 else weights
                    W_ = batched_local_train(Xu, yu, w['cvar_tilt'], LOCAL_EPOCHS)
                    w['cvar_tilt'] = tilt @ W_
                    tt['cvar_tilt'] -= ETA_T * (1.0 - g) * (1.0 - (weights @ active) / a)

                for v in VARIANTS:
                    if dead[v]:
                        L[v].append(CAP); continue
                    lv = global_loss_vec(w[v], X_all, y_all, p)
                    if not np.isfinite(lv) or lv > CAP:
                        lv = CAP; dead[v] = True
                    L[v].append(lv)

            for v in VARIANTS:
                res[v]['overall'].append(np.mean(L[v][-TAIL:]))
                res[v]['inf'].append(group_loss(w[v], X_all, y_all, p, infeas_mask)
                                     if not dead[v] else CAP)
                res[v]['feas'].append(group_loss(w[v], X_all, y_all, p, ~infeas_mask)
                                      if not dead[v] else CAP)
                best_curves[(a, g, v)] = best_curves.get((a, g, v), []) + [L[v]]
        results[(a, g)] = res
        line = " | ".join(f"{v}={np.mean(res[v]['overall']):.2f}" for v in VARIANTS)
        print(f"a={a} g={g} ({time.time()-t0:.0f}s): {line}")

# ================================================================
# Summary table
# ================================================================
avot_final = np.mean([np.mean(c[-TAIL:]) for c in base_curves['avot']])
full_final = np.mean([np.mean(c[-TAIL:]) for c in base_curves['full']])
print(f"\n=== GRID SUMMARY (tail-{TAIL} p-weighted MSE, mean over {len(SEEDS)} seeds) ===")
print(f"baselines: FedAVOT {avot_final:.2f} | FedAvg(full) {full_final:.2f}")
print(f"{'a':>5} {'g':>5} | " + " | ".join(f"{v:>28}" for v in VARIANTS))
for a in ALPHAS:
    for g in GAMMAS:
        cells = []
        for v in VARIANTS:
            o = np.mean(results[(a, g)][v]['overall'])
            i = np.mean(results[(a, g)][v]['inf'])
            cells.append(f"{o:10.2f} (inf-grp {i:9.2f})" if o < CAP else f"{'DIVERGED':>28}")
        print(f"{a:>5} {g:>5} | " + " | ".join(cells))

# best config per variant
print("\nbest per variant:")
best = {}
for v in VARIANTS:
    key = min(results, key=lambda k: np.mean(results[k][v]['overall']))
    best[v] = key
    o = results[key][v]
    print(f"  {v}: a={key[0]}, g={key[1]} -> overall {np.mean(o['overall']):.2f} ± {np.std(o['overall']):.2f}, "
          f"inf-group {np.mean(o['inf']):.2f}, feas-group {np.mean(o['feas']):.2f}")

np.savez(f"data/imdbwiki_cvar_grid_K{K}_{ROUNDS}rounds.npz",
         alphas=ALPHAS, gammas=GAMMAS, seeds=SEEDS,
         **{f"{v}_a{a}_g{g}_{m}": np.array(results[(a, g)][v][m])
            for v in VARIANTS for a in ALPHAS for g in GAMMAS for m in ('overall', 'inf', 'feas')},
         avot=np.array([np.mean(c[-TAIL:]) for c in base_curves['avot']]),
         full=np.array([np.mean(c[-TAIL:]) for c in base_curves['full']]))

# ================================================================
# Figure: best config of each variant vs baselines
# ================================================================
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(ROUNDS)
for label, curves, color in (("FedAVOT", base_curves['avot'], "tab:blue"),
                             ("FedAvg (full)", base_curves['full'], "tab:red")):
    mean = np.mean(curves, axis=0)
    ax.plot(x, mean, label=label, color=color, lw=1.6)
VSTYLE = {'cvar_avot': ("FedAVOT + CVaR (literal)", "tab:green"),
          'cvar_unif': ("FedCVaR, uniform agg", "tab:purple"),
          'cvar_tilt': ("FedAVOT × CVaR tilt (ours)", "tab:olive")}
for v, (label, color) in VSTYLE.items():
    a, g = best[v]
    mean = np.mean(best_curves[(a, g, v)], axis=0)
    ax.plot(x, mean, label=f"{label}, best (α={a}, γ={g})", color=color, lw=1.6)
ax.set_yscale("log")
lo = 0.85 * min(np.mean(base_curves['full'], axis=0).min(), 70)
ax.set_ylim(lo, 300)
ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
ax.set_title(f"IMDb-Wiki, INFEASIBLE regime: CVaR (α,γ) grid — best configs vs baselines\n"
             f"{ROUNDS} rounds, {len(SEEDS)} seeds")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.savefig(f"figures/imdbwiki_cvar_grid_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/imdbwiki_cvar_grid_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/imdbwiki_cvar_grid_K{K}_{ROUNDS}rounds.png")
