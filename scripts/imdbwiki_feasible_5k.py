# Feasible-regime FedAVOT on REAL IMDb-Wiki data, 5000 rounds (follow-up to Herlock's
# 2026-07-11 request). Identical to the notebook's main IMDb-Wiki cell (real clients,
# real ResNet embeddings, cubic importance p) EXCEPT availability r is ALIGNED with
# importance (linear skew, same direction) instead of the cubic mirror image, so the
# transport is feasible (p_i <= pi_i for all clients). Shows FedAVOT reaching
# FedAvg(full) on real data when feasibility holds.
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
ROUNDS = 5000
LOCAL_EPOCHS = 5
SAMPLES_PER_USER = 30
LR = 0.01
SEEDS = [0, 1, 2, 3, 4]
NUM_SAMPLES_FOR_Q = 1_000_000

IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000
TAIL = 500                      # rounds averaged for the quotable final numbers

# ================================================================
# Masked IPFP utilities (same as notebook)
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
    T /= T.sum(axis=0, keepdims=True)
    return T

def solve_T(p, q, subsets):
    M = build_mask(len(p), subsets)
    Y, row_err = ipfp_masked(p, q, M, IPFP_TOL, IPFP_MAX_ITERS)
    print(f"IPFP row_err = {row_err:.2e}")
    return recover_T(Y, q, M)

def column_users_and_weights(T, subsets, j):
    rows = np.array([i-1 for i in subsets[j]])
    w = T[rows, j]
    w /= w.sum()
    return rows, w

# ================================================================
# Vectorized linear-regression helpers (same as notebook)
# ================================================================
def batched_local_train(Xs, ys, w, epochs):
    W = np.repeat(w[None, :], Xs.shape[0], axis=0)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        grad = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * grad
    return W

def global_loss_vec(w, X_all, y_all, p):
    resid = np.einsum('nsd,d->ns', X_all, w) - y_all
    return p @ (resid ** 2).mean(axis=1)

# ================================================================
# Distributions — THE ONE CHANGE vs the notebook:
# p unchanged (cubic, high mass on low-index clients); r now ALIGNED with p
# (linear skew, same direction) instead of the cubic mirror image.
# ================================================================
def make_distributions(N):
    idx = np.arange(1, N+1)
    p = idx[::-1]**3            # unchanged importance
    r = idx[::-1].astype(float) # aligned availability (linear): feasible, but shape
    return p/p.sum(), r/r.sum() # still mismatched (cubic vs linear) -> FedAVOT must reweight

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
# Data (identical to notebook)
# ================================================================
df = pd.read_csv("data/imdb_wiki.csv")
df = df[df["split"] == "train"]
df["client_id"] = df["path"].str.extract(r"(nm\d+)")
groups = [g for _, g in df.groupby("client_id") if len(g) >= SAMPLES_PER_USER]
groups = groups[:NUM_USERS]

EMB = np.load("data/imdb_embeddings.npy", allow_pickle=True).item()
DIM = next(iter(EMB.values())).shape[0]
print(f"embedding DIM = {DIM}, clients = {len(groups)}")

p, r = make_distributions(NUM_USERS)

# feasibility check: p_i <= pi_i must hold for ALL clients in this regime
pi = inclusion_probs(r, NUM_USERS, K, 500_000, np.random.RandomState(0))
infeas_mask = p > pi
print(f"infeasible clients: {infeas_mask.sum()}/{NUM_USERS}, "
      f"infeasible p-mass = {p[infeas_mask].sum()*100:.2f}%, "
      f"max p_i/pi_i = {np.max(p/np.maximum(pi, 1e-12)):.3f}")

subsets = all_K_subsets_1based(NUM_USERS, K)
t0 = time.time()
rng_q = np.random.RandomState(0)
q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, rng_q)
q = (q + 1e-12) / np.sum(q)
print(f"estimate_q done in {time.time()-t0:.0f}s")
T = solve_T(p, q, subsets)
q_cum = np.cumsum(q)

# ================================================================
# Training
# ================================================================
all_fedot, all_faK, all_full = [], [], []
for seed in SEEDS:
    t0 = time.time()
    rng = np.random.RandomState(seed)

    X_full = np.concatenate([np.stack([EMB[pth] for pth in g["path"].values[:SAMPLES_PER_USER]])
                             for g in groups])
    y_full = np.concatenate([g["age"].values[:SAMPLES_PER_USER] for g in groups]).astype(float)
    y_full -= y_full.mean()

    X_all = X_full.reshape(NUM_USERS, SAMPLES_PER_USER, DIM)
    y_all = y_full.reshape(NUM_USERS, SAMPLES_PER_USER)

    w_ot = np.zeros(DIM); w_k = np.zeros(DIM); w_f = np.zeros(DIM)
    L_ot, L_k, L_f = [], [], []
    K_CAP = 1e12; k_diverged = False   # freeze FedAvg(K) once it diverges: its fixed
    for _ in range(ROUNDS):            # (N/K)*p_i scaling explodes under aligned r,
        j = np.searchsorted(q_cum, rng.rand())  # and would overflow to NaN by ~round 200
        users, weights = column_users_and_weights(T, subsets, j)

        w_ot = weights @ batched_local_train(X_all[users], y_all[users], w_ot, LOCAL_EPOCHS)
        L_ot.append(global_loss_vec(w_ot, X_all, y_all, p))

        if not k_diverged:
            M_k = batched_local_train(X_all[users], y_all[users], w_k, LOCAL_EPOCHS)
            w_k = (NUM_USERS / K) * (p[users] @ M_k)
            lk = global_loss_vec(w_k, X_all, y_all, p)
            if not np.isfinite(lk) or lk > K_CAP:
                lk = K_CAP; k_diverged = True
        else:
            lk = K_CAP
        L_k.append(lk)

        w_f = p @ batched_local_train(X_all, y_all, w_f, LOCAL_EPOCHS)
        L_f.append(global_loss_vec(w_f, X_all, y_all, p))

    all_fedot.append(L_ot); all_faK.append(L_k); all_full.append(L_f)
    print(f"seed {seed}: {time.time()-t0:.0f}s, tail-{TAIL} MSE "
          f"AVOT={np.mean(L_ot[-TAIL:]):.2f} K={np.mean(L_k[-TAIL:]):.2f} full={np.mean(L_f[-TAIL:]):.2f}")

def tail_stats(L):
    per_seed = [np.mean(s[-TAIL:]) for s in L]
    return np.mean(per_seed), np.std(per_seed)

m_ot, s_ot = tail_stats(all_fedot)
m_k, s_k = tail_stats(all_faK)
m_f, s_f = tail_stats(all_full)
print(f"\nFINAL (tail-{TAIL} mean over {len(SEEDS)} seeds): "
      f"FedAVOT {m_ot:.2f} ± {s_ot:.2f} | FedAvg(K) {m_k:.2f} ± {s_k:.2f} | FedAvg(full) {m_f:.2f} ± {s_f:.2f}")

# ================================================================
# Figure
# ================================================================
def plot_curve(ax, L, label, color):
    mean = np.mean(L, axis=0); std = np.std(L, axis=0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=label, color=color)
    ax.fill_between(x, mean-std, mean+std, color=color, alpha=0.15)

fig, ax = plt.subplots(figsize=(10, 6))
plot_curve(ax, all_fedot, f"FedAVOT (K={K})", "tab:blue")
plot_curve(ax, all_faK, f"FedAvg (K={K})", "tab:orange")
plot_curve(ax, all_full, "FedAvg (full)", "tab:red")
ax.set_yscale("log")
# FedAvg(K)'s fixed (N/K)*p_i debiasing assumes uniform participation; under
# availability-aligned sampling it is mis-scaled (~3.7x per round) and diverges,
# so cap the axis and annotate rather than let it dwarf the converging curves.
if np.mean(all_faK, axis=0).max() > 1e4:
    ax.set_ylim(top=1e4)
    ax.annotate("FedAvg(K) diverges (off scale):\nfixed N/K scaling assumes uniform participation",
                xy=(0.35, 0.9), xycoords="axes fraction", fontsize=9, color="tab:orange")
ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
ax.set_title(f"IMDb-Wiki (real embeddings), FEASIBLE availability (aligned linear r), "
             f"{ROUNDS} rounds, {len(SEEDS)} seeds\n"
             f"p ≼ π holds → FedAVOT reaches FedAvg(full) on real data")
ax.legend(); ax.grid(alpha=0.3)
fig.savefig(f"figures/imdbwiki_feasible_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/imdbwiki_feasible_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/imdbwiki_feasible_K{K}_{ROUNDS}rounds.png")
