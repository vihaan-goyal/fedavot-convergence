# Bridge between Sec 3.3 theory and the IMDb-Wiki infeasible experiment
# (complete_tex_review.md, Problem 2). The paper's bound (eq. infeasible-rate):
#
#   E[F_p(theta_T) - F_p(theta*)] <= DG/sqrt(T) + 2B*||p - p_hat||_1
#
# where p_hat is the surrogate marginal the stalled IPFP actually delivers.
# The experiments never report p_hat or check the bound. This script computes:
#
#   1. p_hat = Y.sum(axis=1) for the mirrored IMDb-Wiki regime (N=100, K=3).
#      Because IPFP's last scaling step matches the column marginal q exactly,
#      the expected per-round weight of user i is exactly p_hat_i, so this IS
#      the marginal training optimizes under.
#   2. ||p - p_hat||_1, and the same quantity for the synthetic sweep alphas.
#   3. Closed-form least-squares minimizers of F_p and F_p_hat on the real
#      embeddings (the task is linear regression, so theta* is exact), giving
#      the irreducible bias F_p(theta_phat*) - F_p(theta_p*) with NO
#      optimization error mixed in.
#   4. An empirical B (max per-user loss over the relevant iterates) and the
#      resulting bound 2B*||p - p_hat||_1, compared to the measured gap.
#
# No training loop; everything is a property of (p, r, q, IPFP) + closed-form
# regression. Runs in a few minutes (q estimation dominates).
import numpy as np
import pandas as pd
from itertools import combinations
import time

# ================================================================
# Config — MUST match imdbwiki_infeasible_4k.py where shared
# ================================================================
NUM_USERS = 100
K = 3
SAMPLES_PER_USER = 30
NUM_SAMPLES_FOR_Q = 1_000_000
IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000

# measured tail-500 numbers from imdbwiki_infeasible_4k.py (5 seeds)
MEASURED_FEDAVOT = 116.40
MEASURED_FULL = 83.07

# synthetic sweep config (phase_boundary_experiment.py)
SYN_N, SYN_K = 50, 3
SYN_Q_SAMPLES = 300_000
SYN_ALPHAS = [0.5, 1.0, 1.5, 2.0, 3.0]

# ================================================================
# Transport machinery (same as imdbwiki_infeasible_4k.py)
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

def surrogate_marginal(p, r, N, K, q_samples, ipfp_iters):
    """q -> masked IPFP -> p_hat = row sums of the stalled coupling Y."""
    subsets = all_K_subsets_1based(N, K)
    rng_q = np.random.RandomState(0)          # same seed as the training scripts
    q = estimate_q(subsets, r, N, K, q_samples, rng_q)
    q = (q + 1e-12) / np.sum(q)
    M = build_mask(N, subsets)
    Y, row_err = ipfp_masked(p, q, M, IPFP_TOL, ipfp_iters)
    return Y.sum(axis=1), row_err

# ================================================================
# Part 1: IMDb-Wiki mirrored regime — p_hat and ||p - p_hat||_1
# ================================================================
idx = np.arange(1, NUM_USERS+1)
p = (idx[::-1]**3).astype(float); p /= p.sum()
r = (idx**3).astype(float); r /= r.sum()

t0 = time.time()
p_hat, row_err = surrogate_marginal(p, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, IPFP_MAX_ITERS)
gap_l1 = np.abs(p - p_hat).sum()
print(f"[imdb mirrored] IPFP row_err = {row_err:.2e}  ({time.time()-t0:.0f}s)")
print(f"[imdb mirrored] ||p - p_hat||_1 = {gap_l1:.4f}   (p_hat sums to {p_hat.sum():.6f})")

pi = inclusion_probs(r, NUM_USERS, K, 500_000, np.random.RandomState(0))
undeliverable = np.maximum(0.0, p - pi).sum()
print(f"[imdb mirrored] sum max(0, p_i - pi_i) = {undeliverable:.4f} "
      f"(caption's 'undeliverable mass'; p_hat should hug min(p, pi))")
print(f"[imdb mirrored] max|p_hat - min(p, pi)| = {np.max(np.abs(p_hat - np.minimum(p, pi))):.4f}")

# ================================================================
# Part 2: closed-form F_p and F_p_hat minimizers on the real data
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
    """theta* = argmin sum_i w_i * mean_s (x_is . theta - y_is)^2, exact."""
    A = np.einsum('n,nsd,nse->de', w, X_all, X_all) / SAMPLES_PER_USER
    b = np.einsum('n,nsd,ns->d', w, X_all, y_all) / SAMPLES_PER_USER
    return np.linalg.solve(A + 1e-9*np.eye(DIM), b)

def per_user_loss(theta):
    resid = np.einsum('nsd,d->ns', X_all, theta) - y_all
    return (resid**2).mean(axis=1)

theta_p = solve_weighted_ls(p)          # exact minimizer of the target F_p
theta_ph = solve_weighted_ls(p_hat)     # exact minimizer of the surrogate F_p_hat

f_at_p, f_at_ph = per_user_loss(theta_p), per_user_loss(theta_ph)
Fp_star = p @ f_at_p                    # min F_p (unreachable under infeasibility)
Fp_at_ph = p @ f_at_ph                  # target objective at the surrogate optimum
Fph_star = p_hat @ f_at_ph              # min F_p_hat (what training chases)
Fph_at_p = p_hat @ f_at_p

print(f"\n[closed form] F_p(theta_p*)      = {Fp_star:8.2f}   (exact optimum of the target)")
print(f"[closed form] F_p(theta_phat*)   = {Fp_at_ph:8.2f}   (target objective at surrogate optimum)")
print(f"[closed form] F_phat(theta_phat*)= {Fph_star:8.2f}   (surrogate optimum)")
print(f"[closed form] F_phat(theta_p*)   = {Fph_at_p:8.2f}")
print(f"[closed form] irreducible bias F_p(theta_phat*) - F_p(theta_p*) = {Fp_at_ph - Fp_star:.2f}")
print(f"\n[measured]    FedAVOT tail-500 = {MEASURED_FEDAVOT:.2f}, FedAvg(full) tail-500 = {MEASURED_FULL:.2f}, "
      f"gap = {MEASURED_FEDAVOT - MEASURED_FULL:.2f}")

# ================================================================
# Part 3: the bound 2B*||p - p_hat||_1 vs the exact bias
# ================================================================
# The bound comes from |F_p(theta) - F_phat(theta)| <= max_i f_i(theta) * ||p-p_hat||_1
# applied at two points, hence 2B. Empirical B: max per-user loss at the two optima.
B_hat = max(f_at_p.max(), f_at_ph.max())
exact_diff_at_ph = abs((p - p_hat) @ f_at_ph)   # the actual |F_p - F_phat| at theta_phat*
print(f"\n[bound] empirical B = max_i f_i = {B_hat:.1f}")
print(f"[bound] 2B*||p-p_hat||_1 = {2*B_hat*gap_l1:.1f}   (paper's bias term, worst case)")
print(f"[bound] exact |F_p - F_phat| at theta_phat* = {exact_diff_at_ph:.2f} "
      f"= |(p-p_hat) . f(theta_phat*)|")

# ================================================================
# Part 4: ||p - p_hat||_1 across the synthetic sweep (context numbers)
# ================================================================
print("\n[synthetic sweep, N=50 K=3]")
for a in SYN_ALPHAS:
    sidx = np.arange(1, SYN_N+1, dtype=float)
    sp = sidx[::-1]**a; sp /= sp.sum()
    sr = sidx**a; sr /= sr.sum()
    ph_a, err_a = surrogate_marginal(sp, sr, SYN_N, SYN_K, SYN_Q_SAMPLES, 3000)
    print(f"  alpha={a:>3}: ||p - p_hat||_1 = {np.abs(sp - ph_a).sum():.4f}  (row_err {err_a:.1e})")

np.savez("data/imdbwiki_infeasible_bias_check.npz",
         p=p, p_hat=p_hat, pi=pi, gap_l1=gap_l1,
         theta_p=theta_p, theta_phat=theta_ph,
         Fp_star=Fp_star, Fp_at_phat=Fp_at_ph, Fphat_star=Fph_star, B_hat=B_hat)
print("\nsaved data/imdbwiki_infeasible_bias_check.npz")
