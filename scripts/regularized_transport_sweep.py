# Lambda-penalized (unbalanced) masked transport on the INFEASIBLE IMDb-Wiki regime —
# the second half of the Problem-2 bridge (complete_tex_review.md). Sec 3.3 of
# complete.tex claims the bias 2B||p - p_hat||_1 is TUNABLE through the marginal
# penalty lambda in eq. (general-reg-failure); no experiment ever runs that variant.
#
# With cost C = 0 on the mask and entropic scale eps = 1, the KL-penalized problem
#   min_T  KL(T || M) + lambda * KL(T1 || p)   s.t. columns of T sum to q, supp in M
# is solved by unbalanced Sinkhorn (Chizat et al.) on T = diag(u) M diag(v): the row
# update is  u = (p / (M v))^kappa  with  kappa = lambda/(lambda+1),  columns hard.
#   kappa = 1  (lambda = inf)  -> the hard-constraint IPFP all experiments already use
#   kappa = 0  (lambda = 0)    -> ignore p entirely: T is column-uniform, i.e. the
#                                 aggregation IS plain uniform averaging over the drawn
#                                 subset (the CVaR study's surprise winner), p_hat = pi/K
# Sweeping kappa therefore interpolates the paper's regularized family, with our
# existing runs as the kappa=1 endpoint and uniform averaging as the kappa=0 endpoint.
# NOTE the damped variant Y *= (p/rowsum)^kappa is WRONG here: its fixed point is
# kappa-independent (it solves the hard-constraint problem for every kappa > 0), which
# is why a first version of this sweep produced identical marginals for all lambda > 0.
#
# For each kappa this script computes p_hat(kappa) = Y 1, ||p - p_hat||_1, the exact
# closed-form floor F_p(theta_phat*) (linear regression => exact minimizer), and then
# TRAINS FedAVOT with the kappa-plan (all kappas updated in parallel from the same
# subset draw, like the other scripts) to check that the measured loss tracks the
# predicted floor across the whole transition. Companion to infeasible_bias_check.py.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
import time

# ================================================================
# Config — setup identical to imdbwiki_infeasible_4k.py
# ================================================================
NUM_USERS = 100
K = 3
ROUNDS = 4000
LOCAL_EPOCHS = 5
SAMPLES_PER_USER = 30
LR = 0.01
SEEDS = [0, 1, 2]
NUM_SAMPLES_FOR_Q = 1_000_000
SCALE_TOL = 1e-13
SCALE_MAX_ITERS = 2000
TAIL = 500

KAPPAS = [0.0, 0.2, 0.5, 0.8, 0.95, 1.0]   # lambda = kappa/(1-kappa): 0,.25,1,4,19,inf

# ================================================================
# Transport (unbalanced masked Sinkhorn on scaling vectors u, v)
# ================================================================
def all_K_subsets_1based(N, K):
    return list(combinations(range(1, N+1), K))

def penalized_scaling(p, q, subs0, N, kappa, tol, max_iter):
    """T = diag(u) M diag(v) with M the K-subset membership mask, encoded by subs0
    (rows per column). Column marginals hard: v = q/(M^T u); row update is the full
    replacement u = (p/(Mv))^kappa. kappa=1 is plain masked IPFP (stalls when
    infeasible); kappa<1 converges to the lambda-penalized optimum."""
    Kk = subs0.shape[1]
    u = np.ones(N)
    p_hat_prev = None
    for it in range(max_iter):
        v = q / np.maximum(u[subs0].sum(axis=1), 1e-300)     # (M^T u)_j over members
        Mv = np.bincount(subs0.ravel(), weights=np.repeat(v, Kk), minlength=N)
        p_hat = u * Mv                       # row marginal with columns exact
        if p_hat_prev is not None and np.max(np.abs(p_hat - p_hat_prev)) < tol:
            break
        p_hat_prev = p_hat
        if kappa == 0:
            break                            # u stays 1: column-uniform plan is final
        u = (p / np.maximum(Mv, 1e-300)) ** kappa
        u /= u.max()   # plan invariant to u*c, v/c; keeps u in range
    p_hat = p_hat / p_hat.sum()
    row_err = np.max(np.abs(p_hat - p))
    return u, p_hat, row_err, it + 1

def hard_ipfp_dense(p, q, subs0, N, max_iter):
    """Plain masked IPFP on the dense coupling Y — the exact algorithm every other
    script runs. In the infeasible case the scaling-vector form above diverges at
    kappa=1 (relative spread of u overflows), but Y itself stays bounded and stalls
    gracefully, so the kappa=1 endpoint of the sweep uses this form."""
    Mcols = subs0.shape[0]
    M = np.zeros((N, Mcols), dtype=bool)
    for k in range(subs0.shape[1]):
        M[subs0[:, k], np.arange(Mcols)] = True
    Y = np.where(M, (q / M.sum(axis=0))[None, :], 0.0)
    for it in range(max_iter):
        Y *= (p / np.maximum(Y.sum(axis=1), 1e-12))[:, None]
        Y *= (q / np.maximum(Y.sum(axis=0), 1e-12))[None, :]
    p_hat = Y.sum(axis=1)
    p_hat = p_hat / p_hat.sum()
    row_err = np.max(np.abs(p_hat - p))
    return Y, p_hat, row_err, max_iter

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

# ================================================================
# Data + closed-form weighted least squares (as infeasible_bias_check.py)
# ================================================================
df = pd.read_csv("data/imdb_wiki.csv")
df = df[df["split"] == "train"]
df["client_id"] = df["path"].str.extract(r"(nm\d+)")
groups = [g for _, g in df.groupby("client_id") if len(g) >= SAMPLES_PER_USER]
groups = groups[:NUM_USERS]
EMB = np.load("data/imdb_embeddings.npy", allow_pickle=True).item()
DIM = next(iter(EMB.values())).shape[0]

X_full = np.concatenate([np.stack([EMB[pth] for pth in g["path"].values[:SAMPLES_PER_USER]])
                         for g in groups])
y_full = np.concatenate([g["age"].values[:SAMPLES_PER_USER] for g in groups]).astype(float)
y_full -= y_full.mean()
X_all = X_full.reshape(NUM_USERS, SAMPLES_PER_USER, DIM)
y_all = y_full.reshape(NUM_USERS, SAMPLES_PER_USER)

def solve_weighted_ls(w):
    A = np.einsum('n,nsd,nse->de', w, X_all, X_all) / SAMPLES_PER_USER
    b = np.einsum('n,nsd,ns->d', w, X_all, y_all) / SAMPLES_PER_USER
    return np.linalg.solve(A + 1e-9*np.eye(DIM), b)

def per_user_loss(theta):
    resid = np.einsum('nsd,d->ns', X_all, theta) - y_all
    return (resid**2).mean(axis=1)

def batched_local_train(Xs, ys, w, epochs):
    W = np.repeat(w[None, :], Xs.shape[0], axis=0)
    for _ in range(epochs):
        resid = np.einsum('msd,md->ms', Xs, W) - ys
        grad = np.einsum('msd,ms->md', Xs, resid) / ys.shape[1]
        W = W - LR * grad
    return W

def global_loss_vec(w, p):
    resid = np.einsum('nsd,d->ns', X_all, w) - y_all
    return p @ (resid ** 2).mean(axis=1)

# ================================================================
# Distributions + transport per kappa
# ================================================================
idx = np.arange(1, NUM_USERS+1)
p = (idx[::-1]**3).astype(float); p /= p.sum()
r = (idx**3).astype(float); r /= r.sum()

subsets = all_K_subsets_1based(NUM_USERS, K)
subs0 = np.array(subsets) - 1                    # (M, K) 0-based rows per column
t0 = time.time()
q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, np.random.RandomState(0))
q = (q + 1e-12) / np.sum(q)
print(f"estimate_q done in {time.time()-t0:.0f}s")
q_cum = np.cumsum(q)

theta_p = solve_weighted_ls(p)
Fp_star = p @ per_user_loss(theta_p)
print(f"closed-form target optimum F_p(theta_p*) = {Fp_star:.2f}\n")

col_weights = []          # compact (M, K) aggregation weights per kappa
gap_l1, floors, biases = [], [], []
for kappa in KAPPAS:
    t0 = time.time()
    if kappa == 1.0:
        Y, p_hat, row_err, iters = hard_ipfp_dense(p, q, subs0, NUM_USERS, 1000)
        W = np.stack([Y[subs0[:, k], np.arange(len(subsets))] for k in range(K)], axis=1)
        del Y
    else:
        u, p_hat, row_err, iters = penalized_scaling(p, q, subs0, NUM_USERS, kappa,
                                                     SCALE_TOL, SCALE_MAX_ITERS)
        W = u[subs0]             # column weight of user i in subset j is prop. to u_i
    s = W.sum(axis=1, keepdims=True)
    W = np.where(s > 0, W / np.maximum(s, 1e-300), 1.0 / K)   # underflowed columns
    col_weights.append(W)                                     # (q ~ 1e-12, never drawn)
    theta_ph = solve_weighted_ls(p_hat)
    L_ph = per_user_loss(theta_ph)
    g1 = np.abs(p - p_hat).sum()
    floor = p @ L_ph
    bias = abs((p - p_hat) @ L_ph)
    gap_l1.append(g1); floors.append(floor); biases.append(bias)
    lam = "inf" if kappa == 1.0 else f"{kappa/(1-kappa):.2g}"
    print(f"kappa={kappa:<5} (lambda={lam:>4}): iters={iters:<5} row_err={row_err:.1e}  "
          f"||p-p_hat||_1={g1:.4f}  predicted floor F_p(theta_phat*)={floor:7.2f}  "
          f"exact bias={bias:6.2f}  ({time.time()-t0:.0f}s)")

# ================================================================
# Training: all kappa-plans + full participation in parallel per draw
# ================================================================
n_k = len(KAPPAS)
all_L = [[] for _ in range(n_k)]     # per kappa: list over seeds of loss curves
all_full = []
for seed in SEEDS:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    w_k = [np.zeros(DIM) for _ in range(n_k)]
    w_f = np.zeros(DIM)
    L_k = [[] for _ in range(n_k)]
    L_f = []
    for _ in range(ROUNDS):
        j = np.searchsorted(q_cum, rng.rand())
        users = subs0[j]
        for m in range(n_k):
            w_k[m] = col_weights[m][j] @ batched_local_train(X_all[users], y_all[users],
                                                             w_k[m], LOCAL_EPOCHS)
            L_k[m].append(global_loss_vec(w_k[m], p))
        w_f = p @ batched_local_train(X_all, y_all, w_f, LOCAL_EPOCHS)
        L_f.append(global_loss_vec(w_f, p))
    for m in range(n_k):
        all_L[m].append(L_k[m])
    all_full.append(L_f)
    tails = " ".join(f"k{KAPPAS[m]}={np.mean(L_k[m][-TAIL:]):.1f}" for m in range(n_k))
    print(f"seed {seed}: {time.time()-t0:.0f}s  tail-{TAIL}: {tails} full={np.mean(L_f[-TAIL:]):.2f}")

meas_mean, meas_std = [], []
for m in range(n_k):
    per_seed = [np.mean(s[-TAIL:]) for s in all_L[m]]
    meas_mean.append(np.mean(per_seed)); meas_std.append(np.std(per_seed))
full_mean = np.mean([np.mean(s[-TAIL:]) for s in all_full])

print(f"\n{'kappa':>6} {'lambda':>7} {'||p-p_hat||_1':>14} {'predicted floor':>16} "
      f"{'measured':>16}")
for m, kappa in enumerate(KAPPAS):
    lam = "inf" if kappa == 1.0 else f"{kappa/(1-kappa):.2g}"
    print(f"{kappa:>6} {lam:>7} {gap_l1[m]:>14.4f} {floors[m]:>16.2f} "
          f"{meas_mean[m]:>10.2f} ± {meas_std[m]:.2f}")
print(f"full participation: measured {full_mean:.2f}, closed form {Fp_star:.2f}")

# ================================================================
# Figure + saved curves
# ================================================================
np.savez(f"data/imdbwiki_regularized_K{K}_{ROUNDS}rounds_curves.npz",
         kappas=np.array(KAPPAS), gap_l1=np.array(gap_l1), floors=np.array(floors),
         biases=np.array(biases), meas_mean=np.array(meas_mean),
         meas_std=np.array(meas_std), Fp_star=Fp_star, full_mean=full_mean,
         curves=np.array([[s for s in all_L[m]] for m in range(n_k)]),
         full_curves=np.array(all_full), p=p, r=r)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.6))
x = np.array(KAPPAS)

ax1.plot(x, gap_l1, "o-", color="tab:blue", label=r"$\|p-\hat{p}(\lambda)\|_1$ (left)")
ax1.set_xlabel(r"$\kappa = \lambda/(\lambda+\varepsilon)$")
ax1.set_ylabel(r"$\|p-\hat{p}\|_1$", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.set_ylim(0, 2)
ax1b = ax1.twinx()
ax1b.plot(x, biases, "s--", color="tab:green",
          label=r"exact bias $|(p-\hat{p})^\top L(\theta^\dagger)|$ (right)")
ax1b.set_ylabel(r"exact bias term", color="tab:green")
ax1b.tick_params(axis="y", labelcolor="tab:green")
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax1b.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=9, loc="center right")
ax1.set_title("Marginal gap barely moves with penalty strength")
ax1.grid(alpha=0.3)

ax2.errorbar(x, meas_mean, yerr=meas_std, fmt="o-", color="tab:blue",
             label=f"FedAVOT measured (tail-{TAIL}, {len(SEEDS)} seeds)")
ax2.plot(x, floors, "k--", marker="s",
         label=r"predicted floor $F_p(\theta^\dagger(\lambda))$ (closed form)")
ax2.axhline(full_mean, color="tab:red", lw=1.4, label="FedAvg (full), measured")
ax2.annotate("uniform\naveraging", xy=(x[0], meas_mean[0]), xytext=(0.04, 111.5),
             fontsize=8.5, color="tab:blue",
             arrowprops=dict(arrowstyle="-", color="tab:blue", lw=0.8))
ax2.annotate("plain masked IPFP\n(all other experiments)", xy=(x[-1], meas_mean[-1]),
             xytext=(0.52, 119.0), fontsize=8.5, color="tab:blue",
             arrowprops=dict(arrowstyle="-", color="tab:blue", lw=0.8))
ax2.set_ylim(82, 122)
ax2.set_xlabel(r"$\kappa = \lambda/(\lambda+\varepsilon)$")
ax2.set_ylabel("Global p-weighted MSE")
ax2.set_title("Flat bias floor; variance overhead grows with penalty")
ax2.grid(alpha=0.3); ax2.legend(fontsize=9, loc="center left")

fig.suptitle(f"IMDb-Wiki mirrored (infeasible) regime: lambda-penalized transport sweep, "
             f"K={K}, {ROUNDS} rounds", y=1.02)
fig.tight_layout()
fig.savefig(f"figures/imdbwiki_regularized_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/imdbwiki_regularized_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/imdbwiki_regularized_K{K}_{ROUNDS}rounds.png / .pdf")
