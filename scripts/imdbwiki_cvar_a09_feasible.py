# CVaR x FedAVOT study in the FEASIBLE IMDb-Wiki regime (aligned linear r), companion to
# imdbwiki_cvar_fedavot.py (infeasible/mirrored). Herlock 2026-07-11: "Infeasible case,
# and feasible!? Both!?" Same CVaR config as the infeasible run (alpha=0.3, gamma=0.3,
# eta_t=0.05), same seeds, 4000 rounds, so the two figures are directly comparable.
# Methods (parallel, same draws): FedAVOT (blue), FedAVOT+CVaR (green),
# FedCVaR uniform agg (purple), FedAvg(full) (red). Divergence guard at 1e12.
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
SEEDS = [0, 1, 2, 3, 4]
NUM_SAMPLES_FOR_Q = 1_000_000
IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000
TAIL = 500

ALPHA_CVAR = 0.9
GAMMA_CVAR = 0.9
ETA_T = 0.05
T0 = 0.0
CAP = 1e12

# ================================================================
# Transport
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

def batched_local_train_cvar(Xs, ys, w, t, epochs):
    m = Xs.shape[0]
    W = np.repeat(w[None, :], m, axis=0)
    Tv = np.full(m, t)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        f = (resid ** 2).mean(axis=1)
        active = (f > Tv).astype(float)
        coef = (1.0 - GAMMA_CVAR) / ALPHA_CVAR * active + GAMMA_CVAR
        grad_w = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * coef[:, None] * grad_w
        Tv = Tv - ETA_T * (1.0 - GAMMA_CVAR) * (1.0 - active / ALPHA_CVAR)
    return W, Tv

def global_loss_vec(w, X_all, y_all, p):
    resid = np.einsum('nsd,d->ns', X_all, w) - y_all
    return p @ (resid ** 2).mean(axis=1)

# ================================================================
# Distributions: cubic importance, ALIGNED linear availability (feasible)
# ================================================================
def make_distributions(N):
    idx = np.arange(1, N+1)
    p = idx[::-1]**3
    r = idx[::-1].astype(float)
    return p/p.sum(), r/r.sum()

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

# ================================================================
# Data
# ================================================================
df = pd.read_csv("data/imdb_wiki.csv")
df = df[df["split"] == "train"]
df["client_id"] = df["path"].str.extract(r"(nm\d+)")
groups = [g for _, g in df.groupby("client_id") if len(g) >= SAMPLES_PER_USER]
groups = groups[:NUM_USERS]
EMB = np.load("data/imdb_embeddings.npy", allow_pickle=True).item()
DIM = next(iter(EMB.values())).shape[0]

p, r = make_distributions(NUM_USERS)
pi = inclusion_probs(r, NUM_USERS, K, 500_000, np.random.RandomState(0))
infeas_mask = p > pi
print(f"infeasible users: {infeas_mask.sum()}/{NUM_USERS}, "
      f"infeasible p-mass = {p[infeas_mask].sum()*100:.2f}% (should be 0: feasible regime)")
print(f"CVaR params: alpha={ALPHA_CVAR}, gamma={GAMMA_CVAR}, eta_t={ETA_T}")

subsets = list(combinations(range(1, NUM_USERS+1), K))
q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, np.random.RandomState(0))
q = (q + 1e-12) / q.sum()
T = solve_T(p, q, subsets)
q_cum = np.cumsum(q)

# ================================================================
# Training
# ================================================================
METHODS = ('avot', 'cvar_avot', 'cvar_unif', 'full')
curves = {k: [] for k in METHODS}
finals = {k: [] for k in METHODS}

for seed in SEEDS:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    X_full = np.concatenate([np.stack([EMB[pth] for pth in g["path"].values[:SAMPLES_PER_USER]])
                             for g in groups])
    y_full = np.concatenate([g["age"].values[:SAMPLES_PER_USER] for g in groups]).astype(float)
    y_full -= y_full.mean()
    X_all = X_full.reshape(NUM_USERS, SAMPLES_PER_USER, DIM)
    y_all = y_full.reshape(NUM_USERS, SAMPLES_PER_USER)

    w = {k: np.zeros(DIM) for k in METHODS}
    t_ca, t_cu = T0, T0
    dead = {k: False for k in METHODS}
    L = {k: [] for k in METHODS}

    for _ in range(ROUNDS):
        j = np.searchsorted(q_cum, rng.rand())
        users, weights = column_users_and_weights(T, subsets, j)
        Xu, yu = X_all[users], y_all[users]

        if not dead['avot']:
            w['avot'] = weights @ batched_local_train(Xu, yu, w['avot'], LOCAL_EPOCHS)
        if not dead['cvar_avot']:
            W_, Tv_ = batched_local_train_cvar(Xu, yu, w['cvar_avot'], t_ca, LOCAL_EPOCHS)
            w['cvar_avot'] = weights @ W_; t_ca = weights @ Tv_
        if not dead['cvar_unif']:
            W_, Tv_ = batched_local_train_cvar(Xu, yu, w['cvar_unif'], t_cu, LOCAL_EPOCHS)
            w['cvar_unif'] = W_.mean(axis=0); t_cu = Tv_.mean()
        w['full'] = p @ batched_local_train(X_all, y_all, w['full'], LOCAL_EPOCHS)

        for k in METHODS:
            if dead[k]:
                L[k].append(CAP); continue
            lv = global_loss_vec(w[k], X_all, y_all, p)
            if not np.isfinite(lv) or lv > CAP:
                lv = CAP; dead[k] = True
            L[k].append(lv)

    for k in METHODS:
        curves[k].append(L[k])
        finals[k].append(np.mean(L[k][-TAIL:]))
    print(f"seed {seed}: {time.time()-t0:.0f}s, t_ca={t_ca:.1f}, tail-{TAIL} "
          + " ".join(f"{k}={np.mean(L[k][-TAIL:]):.2f}" for k in METHODS))

print(f"\nFINAL (tail-{TAIL} mean ± std over {len(SEEDS)} seeds):")
for k in METHODS:
    print(f"  {k:10s}: {np.mean(finals[k]):10.2f} ± {np.std(finals[k]):.2f}")

np.savez(f"data/imdbwiki_cvar_feasible_a09_K{K}_{ROUNDS}rounds_curves.npz",
         **{k: np.array(v) for k, v in curves.items()},
         p=p, r=r, pi=pi, alpha=ALPHA_CVAR, gamma=GAMMA_CVAR, eta_t=ETA_T)

# ================================================================
# Figure
# ================================================================
STYLE = {'avot':      ("FedAVOT",                                     "tab:blue"),
         'cvar_avot': (f"FedAVOT + CVaR (α={ALPHA_CVAR}, γ={GAMMA_CVAR})",       "tab:green"),
         'cvar_unif': (f"FedCVaR, uniform agg (α={ALPHA_CVAR}, γ={GAMMA_CVAR})", "tab:purple"),
         'full':      ("FedAvg (full)",                               "tab:red")}

fig, ax = plt.subplots(figsize=(10, 6))
for k, (label, color) in STYLE.items():
    mean = np.mean(curves[k], axis=0); std = np.std(curves[k], axis=0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=label, color=color, lw=1.6)
    ax.fill_between(x, np.maximum(mean-std, 1e-3), mean+std, color=color, alpha=0.12)
ax.set_yscale("log")
lo = 0.85 * min(np.mean(curves['avot'], axis=0).min(), np.mean(curves['full'], axis=0).min())
hi = 1.6 * max(np.mean(curves['avot'], axis=0).max(), np.mean(curves['full'], axis=0).max())
ax.set_ylim(lo, hi)
ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
ax.set_title(f"IMDb-Wiki, FEASIBLE regime (aligned linear r), {ROUNDS} rounds, {len(SEEDS)} seeds\n"
             f"CVaR study in the feasible case (companion to the infeasible figure)")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.savefig(f"figures/imdbwiki_cvar_feasible_a09_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/imdbwiki_cvar_feasible_a09_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/imdbwiki_cvar_feasible_a09_K{K}_{ROUNDS}rounds.png")
