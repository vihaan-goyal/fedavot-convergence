# FedAVOT + FED-CVaR-AVG (arXiv:2309.14176, Theodoropoulos/Nikolakakis/Kalogerias) in the
# INFEASIBLE IMDb-Wiki regime -- Herlock's 2026-07-11 request: combine the risk-aware CVaR
# objective with FedAVOT and see whether it recovers part of the unreachable-mass floor.
#
# Local objective per user (paper eq. 6):
#   G_i(theta, t) = (1-gamma)*[ t + (1/alpha)*(f_i(theta) - t)_+ ] + gamma*f_i(theta)
# Users run H local GD epochs on (theta, t); alpha=1 (or gamma=1) reduces to risk-neutral.
# Combination: aggregation of BOTH theta and t uses FedAVOT transport weights.
#
# Methods (updated in parallel from the same subset draws, mirrored cubic p/r as in
# imdbwiki_infeasible_4k.py):
#   FedAVOT              (risk-neutral, transport weights)          - blue
#   FedAVOT + CVaR       (risk-aware, transport weights)            - green
#   FedCVaR (uniform)    (risk-aware, uniform mean over S -- paper-style RAM-agnostic) - purple
#   FedAvg (full)        (risk-neutral reference optimum on F)      - red
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
LR = 0.01                      # eta_theta (same as all IMDb-Wiki runs)
SEEDS = [0, 1, 2, 3, 4]
NUM_SAMPLES_FOR_Q = 1_000_000

IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000
TAIL = 500

# --- CVaR hyper-parameters (paper's MNIST setting; alpha=0.1 makes the transport-
# weighted combination unstable here: 9.1x hinge multiplier on top of extreme
# transport weights -> loss spikes; 0.3/0.3 is stable) ---
ALPHA_CVAR = 0.9
GAMMA_CVAR = 0.9
ETA_T = 0.05        # paper uses eta_t ~ eta_theta/20 on ~O(1) losses; our MSE is O(100),
T0 = 0.0            # so eta_t is scaled up to let t reach the loss scale within the run

# ================================================================
# Masked IPFP utilities (as in the notebook)
# ================================================================
def build_mask(n, subsets):
    M = np.zeros((n, len(subsets)), dtype=bool)
    for j, s in enumerate(subsets):
        for i in s:
            M[i-1, j] = True
    return M

def initialize_Y(p, q, M):
    Y = np.zeros_like(M, dtype=float)
    for j in range(M.shape[1]):
        rows = np.where(M[:, j])[0]
        if rows.size > 0:
            Y[rows, j] = q[j] / len(rows)
    return Y

def ipfp_masked(p, q, M, tol, max_iter):
    Y = initialize_Y(p, q, M)
    row_err = np.inf
    for _ in range(max_iter):
        Y *= (p / np.maximum(Y.sum(axis=1), 1e-12))[:, None]
        Y *= (q / np.maximum(Y.sum(axis=0), 1e-12))[None, :]
        row_err = np.max(np.abs(Y.sum(axis=1) - p))
        if row_err < tol:
            break
    return Y, row_err

def recover_T(Y, q, M):
    T = np.zeros_like(Y)
    for j in range(len(q)):
        if q[j] > 0:
            T[:, j] = Y[:, j] / q[j]
    T[~M] = 0
    s = T.sum(axis=0, keepdims=True); s[s == 0] = 1.0
    T /= s
    return T

def solve_T(p, q, subsets):
    M = build_mask(len(p), subsets)
    Y, row_err = ipfp_masked(p, q, M, IPFP_TOL, IPFP_MAX_ITERS)
    print(f"IPFP row_err = {row_err:.2e}")
    return recover_T(Y, q, M)

def column_users_and_weights(T, subsets, j):
    rows = np.array([i-1 for i in subsets[j]])
    w = T[rows, j]
    ss = w.sum()
    return rows, (w/ss if ss > 0 else np.full(len(rows), 1.0/len(rows)))

# ================================================================
# Learners
# ================================================================
def batched_local_train(Xs, ys, w, epochs):
    # risk-neutral local GD (as in all other scripts)
    W = np.repeat(w[None, :], Xs.shape[0], axis=0)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        grad = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * grad
    return W

def batched_local_train_cvar(Xs, ys, w, t, epochs):
    # local GD on G_i(theta, t) = (1-g)[t + (f_i - t)_+/a] + g f_i for each of m users,
    # all starting from the same global (w, t). Returns (m,DIM) thetas and (m,) t's.
    m = Xs.shape[0]
    W = np.repeat(w[None, :], m, axis=0)
    Tv = np.full(m, t)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        f = (resid ** 2).mean(axis=1)                     # (m,) local MSE
        active = (f > Tv).astype(float)                   # hinge indicator 1{f_i > t}
        coef = (1.0 - GAMMA_CVAR) / ALPHA_CVAR * active + GAMMA_CVAR
        grad_w = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * coef[:, None] * grad_w
        Tv = Tv - ETA_T * (1.0 - GAMMA_CVAR) * (1.0 - active / ALPHA_CVAR)
    return W, Tv

def global_loss_vec(w, X_all, y_all, p):
    resid = np.einsum('nsd,d->ns', X_all, w) - y_all
    return p @ (resid ** 2).mean(axis=1)

def group_loss(w, X_all, y_all, p, mask):
    # p-weighted MSE restricted to a user group, renormalized within the group
    resid = np.einsum('nsd,d->ns', X_all[mask], w) - y_all[mask]
    pm = p[mask]
    return pm @ (resid ** 2).mean(axis=1) / pm.sum()

# ================================================================
# Distributions (mirrored cubic = INFEASIBLE, as in the notebook)
# ================================================================
def make_distributions(N):
    idx = np.arange(1, N+1)
    p = idx[::-1]**3
    r = (idx**3).astype(float)
    return p/p.sum(), r/r.sum()

def all_K_subsets_1based(N, K):
    return list(combinations(range(1, N+1), K))

def estimate_q(subsets, r, N, K, samples, rng):
    lookup = {s: i for i, s in enumerate(subsets)}
    counts = np.zeros(len(subsets))
    logr = np.log(r)
    done = 0
    while done < samples:
        b = min(50_000, samples - done)
        g = rng.gumbel(size=(b, N)) + logr[None, :]
        tk = np.argpartition(-g, K, axis=1)[:, :K]
        tk.sort(axis=1)
        for row in tk + 1:
            counts[lookup[tuple(row.tolist())]] += 1
        done += b
    return counts / counts.sum()

def inclusion_probs(r, N, K, samples, rng):
    g = rng.gumbel(size=(samples, N)) + np.log(r)[None, :]
    tk = np.argpartition(-g, K, axis=1)[:, :K]
    incl = np.zeros(N)
    np.add.at(incl, tk.ravel(), 1)
    return incl / samples

# ================================================================
# Data (identical to the other IMDb-Wiki scripts)
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
      f"infeasible p-mass = {p[infeas_mask].sum()*100:.2f}%")
print(f"CVaR params: alpha={ALPHA_CVAR}, gamma={GAMMA_CVAR}, eta_t={ETA_T}")

subsets = all_K_subsets_1based(NUM_USERS, K)
rng_q = np.random.RandomState(0)
q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, rng_q)
q = (q + 1e-12) / np.sum(q)
T = solve_T(p, q, subsets)
q_cum = np.cumsum(q)

# ================================================================
# Training
# ================================================================
curves = {k: [] for k in ('avot', 'cvar_avot', 'cvar_unif', 'full')}
finals = {k: [] for k in ('avot', 'cvar_avot', 'cvar_unif', 'full')}
group_finals = {k: {'inf': [], 'feas': []} for k in ('avot', 'cvar_avot', 'cvar_unif', 'full')}

for seed in SEEDS:
    t0 = time.time()
    rng = np.random.RandomState(seed)

    X_full = np.concatenate([np.stack([EMB[pth] for pth in g["path"].values[:SAMPLES_PER_USER]])
                             for g in groups])
    y_full = np.concatenate([g["age"].values[:SAMPLES_PER_USER] for g in groups]).astype(float)
    y_full -= y_full.mean()
    X_all = X_full.reshape(NUM_USERS, SAMPLES_PER_USER, DIM)
    y_all = y_full.reshape(NUM_USERS, SAMPLES_PER_USER)

    w = {k: np.zeros(DIM) for k in curves}
    t_ca, t_cu = T0, T0                      # global CVaR thresholds (combined / uniform)
    L = {k: [] for k in curves}

    for _ in range(ROUNDS):
        j = np.searchsorted(q_cum, rng.rand())
        users, weights = column_users_and_weights(T, subsets, j)

        # FedAVOT (risk-neutral)
        w['avot'] = weights @ batched_local_train(X_all[users], y_all[users], w['avot'], LOCAL_EPOCHS)

        # FedAVOT + CVaR: local G_i training, transport-weighted aggregation of theta AND t
        W_ca, Tv_ca = batched_local_train_cvar(X_all[users], y_all[users], w['cvar_avot'], t_ca, LOCAL_EPOCHS)
        w['cvar_avot'] = weights @ W_ca
        t_ca = weights @ Tv_ca

        # FedCVaR, uniform mean over S (paper-style RAM-agnostic aggregation)
        W_cu, Tv_cu = batched_local_train_cvar(X_all[users], y_all[users], w['cvar_unif'], t_cu, LOCAL_EPOCHS)
        w['cvar_unif'] = W_cu.mean(axis=0)
        t_cu = Tv_cu.mean()

        # FedAvg(full), risk-neutral reference
        w['full'] = p @ batched_local_train(X_all, y_all, w['full'], LOCAL_EPOCHS)

        for k in curves:
            L[k].append(global_loss_vec(w[k], X_all, y_all, p))

    for k in curves:
        curves[k].append(L[k])
        finals[k].append(np.mean(L[k][-TAIL:]))
        group_finals[k]['inf'].append(group_loss(w[k], X_all, y_all, p, infeas_mask))
        group_finals[k]['feas'].append(group_loss(w[k], X_all, y_all, p, ~infeas_mask))
    print(f"seed {seed}: {time.time()-t0:.0f}s, t_ca={t_ca:.1f}, tail-{TAIL} "
          + " ".join(f"{k}={np.mean(L[k][-TAIL:]):.2f}" for k in curves))

print(f"\nFINAL (tail-{TAIL} mean Â± std over {len(SEEDS)} seeds):")
for k in curves:
    print(f"  {k:10s}: overall {np.mean(finals[k]):7.2f} Â± {np.std(finals[k]):.2f} | "
          f"infeasible-group {np.mean(group_finals[k]['inf']):7.2f} Â± {np.std(group_finals[k]['inf']):.2f} | "
          f"feasible-group {np.mean(group_finals[k]['feas']):7.2f} Â± {np.std(group_finals[k]['feas']):.2f}")

np.savez(f"data/imdbwiki_cvar_a09_K{K}_{ROUNDS}rounds_curves.npz",
         **{k: np.array(v) for k, v in curves.items()},
         p=p, r=r, pi=pi, infeas_mask=infeas_mask,
         alpha=ALPHA_CVAR, gamma=GAMMA_CVAR, eta_t=ETA_T)

# ================================================================
# Figure
# ================================================================
STYLE = {'avot':      ("FedAVOT",                     "tab:blue"),
         'cvar_avot': (f"FedAVOT + CVaR (α={ALPHA_CVAR}, γ={GAMMA_CVAR})", "tab:green"),
         'cvar_unif': (f"FedCVaR, uniform agg (α={ALPHA_CVAR}, γ={GAMMA_CVAR})", "tab:purple"),
         'full':      ("FedAvg (full)",                "tab:red")}

fig, ax = plt.subplots(figsize=(10, 6))
for k, (label, color) in STYLE.items():
    mean = np.mean(curves[k], axis=0); std = np.std(curves[k], axis=0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=label, color=color, lw=1.6)
    ax.fill_between(x, np.maximum(mean-std, 1e-3), mean+std, color=color, alpha=0.12)
ax.set_yscale("log")
ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
ax.set_title(f"IMDb-Wiki, INFEASIBLE regime (mirrored cubic r), {ROUNDS} rounds, {len(SEEDS)} seeds\n"
             f"Does the CVaR risk-aware objective (arXiv:2309.14176) recover part of the floor?")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.savefig(f"figures/imdbwiki_cvar_a09_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/imdbwiki_cvar_a09_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/imdbwiki_cvar_a09_K{K}_{ROUNDS}rounds.png")

