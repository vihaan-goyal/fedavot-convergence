# Feasible-regime run extended to 5000 rounds (Herlock's request, 2026-07-11).
# Identical setup to the LEFT panel of phase_boundary_experiment.py (alpha=0.5),
# only ROUNDS is raised 1500 -> 5000. Single-panel figure.
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt

# ---------------- config ----------------
NUM_USERS, K = 50, 3
ROUNDS, EVAL_EVERY = 5000, 25
LOCAL_EPOCHS, DIM, SAMPLES_PER_USER = 5, 40, 30
LR = 1e-3
SEEDS = [0, 1, 2]
Q_SAMPLES = 400_000
IPFP_TOL, IPFP_MAX_ITERS = 1e-10, 3000
HET = 3.0
ALPHA = 0.5                                 # feasible regime

# ---------------- transport (guarded) ----------------
def build_mask(n, subsets):
    M = np.zeros((n, len(subsets)), dtype=bool)
    for j, s in enumerate(subsets):
        for i in s: M[i-1, j] = True
    return M

def ipfp_masked(p, q, M, tol, max_iter):
    Y = np.zeros_like(M, dtype=float)
    for j in range(M.shape[1]):
        rows = np.where(M[:, j])[0]
        if rows.size: Y[rows, j] = q[j] / rows.size
    row_err = np.inf
    for _ in range(max_iter):
        Y *= (p / np.maximum(Y.sum(1), 1e-12))[:, None]
        Y *= (q / np.maximum(Y.sum(0), 1e-12))[None, :]
        row_err = np.max(np.abs(Y.sum(1) - p))
        if row_err < tol: break
    return Y, row_err

def solve_T(p, q, subsets):
    M = build_mask(len(p), subsets)
    Y, row_err = ipfp_masked(p, q, M, IPFP_TOL, IPFP_MAX_ITERS)
    T = np.zeros_like(Y); pos = q > 0
    T[:, pos] = Y[:, pos] / q[pos]; T[~M] = 0
    s = T.sum(0, keepdims=True); s[s == 0] = 1.0; T /= s
    return T, row_err

def col_users_weights(T, subsets, j):
    rows = np.array([i-1 for i in subsets[j]])
    w = T[rows, j]; ss = w.sum()
    return rows, (w/ss if ss > 0 else np.full(len(rows), 1.0/len(rows)))

# ---------------- learner ----------------
def local_train(X, y, w, epochs):
    for _ in range(epochs):
        w = w - LR * (X.T @ (X @ w - y) / len(y))
    return w
def global_loss(w, ud, p):
    return sum(p[i]*np.mean((X @ w - y)**2) for i, (X, y) in enumerate(ud))

# ---------------- distributions ----------------
def make_skew(N, a):
    idx = np.arange(1, N+1, dtype=float)
    r = idx**a; p = idx[::-1]**a
    return p/p.sum(), r/r.sum()
def all_K_subsets(N, K): return list(combinations(range(1, N+1), K))

def estimate_q(subsets, r, N, K, samples, rng):          # vectorized Gumbel top-K, no-replacement ~ r
    idx = {s: i for i, s in enumerate(subsets)}
    counts = np.zeros(len(subsets)); done = 0
    while done < samples:
        b = min(50_000, samples - done)
        g = rng.gumbel(size=(b, N)) + np.log(r)[None, :]
        tk = np.argpartition(-g, K, axis=1)[:, :K]; tk.sort(1)
        for row in tk + 1: counts[idx[tuple(row.tolist())]] += 1
        done += b
    return counts / counts.sum()
def inclusion_probs(r, N, K, samples, rng):
    g = rng.gumbel(size=(samples, N)) + np.log(r)[None, :]
    tk = np.argpartition(-g, K, axis=1)[:, :K]
    incl = np.zeros(N); np.add.at(incl, tk.ravel(), 1)
    return incl / samples

# ---------------- run ----------------
p, r = make_skew(NUM_USERS, ALPHA)
subsets = all_K_subsets(NUM_USERS, K)
infeas = p[p > inclusion_probs(r, NUM_USERS, K, 200_000, np.random.RandomState(0))].sum()
print(f"alpha={ALPHA}: infeasible p-mass = {infeas*100:.1f}%")

curves = {'ot': [], 'k': [], 'f': []}
fin = {'ot': [], 'k': [], 'f': []}
for seed in SEEDS:
    rng = np.random.RandomState(seed)
    X = rng.randn(NUM_USERS*SAMPLES_PER_USER, DIM)
    w_shared, direction = rng.randn(DIM), rng.randn(DIM)
    ud = []
    for i in range(NUM_USERS):
        Xi = X[i*SAMPLES_PER_USER:(i+1)*SAMPLES_PER_USER]
        drift = 2.0*i/(NUM_USERS-1) - 1.0
        w_i = w_shared + HET*drift*direction + 0.3*rng.randn(DIM)
        ud.append((Xi, Xi @ w_i + 0.1*rng.randn(SAMPLES_PER_USER)))
    q = estimate_q(subsets, r, NUM_USERS, K, Q_SAMPLES, rng); q = (q+1e-12); q /= q.sum()
    T, row_err = solve_T(p, q, subsets); qc = np.cumsum(q)
    print(f"seed {seed}: IPFP row_err = {row_err:.2e}")
    w_ot = np.zeros(DIM); w_k = np.zeros(DIM); w_f = np.zeros(DIM)
    c_ot, c_k, c_f = [], [], []
    for t in range(ROUNDS):
        j = int(np.searchsorted(qc, rng.rand()))
        users, wts = col_users_weights(T, subsets, j)
        w_ot = sum(a*local_train(*ud[u], w_ot.copy(), LOCAL_EPOCHS) for a, u in zip(wts, users))
        w_k  = sum((NUM_USERS/K)*p[u]*local_train(*ud[u], w_k.copy(), LOCAL_EPOCHS) for u in users)
        w_f  = sum(p[u]*local_train(*ud[u], w_f.copy(), LOCAL_EPOCHS) for u in range(NUM_USERS))
        if t % EVAL_EVERY == 0:
            c_ot.append(global_loss(w_ot, ud, p)); c_k.append(global_loss(w_k, ud, p)); c_f.append(global_loss(w_f, ud, p))
    fin['ot'].append(global_loss(w_ot, ud, p)); fin['k'].append(global_loss(w_k, ud, p)); fin['f'].append(global_loss(w_f, ud, p))
    curves['ot'].append(c_ot); curves['k'].append(c_k); curves['f'].append(c_f)
    print(f"seed {seed}: final AVOT={fin['ot'][-1]:.3f} K={fin['k'][-1]:.3f} full={fin['f'][-1]:.3f}")

mean_curves = {k: np.mean(np.array(v), axis=0) for k, v in curves.items()}
print(f"\nfinal (mean over {len(SEEDS)} seeds): "
      f"AVOT={np.mean(fin['ot']):.3f}  FedAvg(K)={np.mean(fin['k']):.3f}  FedAvg(full)={np.mean(fin['f']):.3f}  "
      f"ratio AVOT/full={np.mean(fin['ot'])/np.mean(fin['f']):.2f}")

# ---------------- figure ----------------
BLUE, ORANGE, RED = "tab:blue", "tab:orange", "tab:red"
fig, ax = plt.subplots(figsize=(6.5, 5))
x = np.arange(len(mean_curves['ot']))*EVAL_EVERY
ax.plot(x, mean_curves['ot'], color=BLUE, lw=2, label="FedAVOT")
ax.plot(x, mean_curves['f'],  color=RED,  lw=2, label="FedAvg (full)")
ax.plot(x, mean_curves['k'],  color=ORANGE, lw=1.3, alpha=0.8, label="FedAvg (K)")
ax.set_yscale("log"); ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
ax.set_title(f"Feasible regime (α={ALPHA}, {infeas*100:.0f}% infeasible), {ROUNDS} rounds\nFedAVOT converges to optimum")
ax.grid(alpha=0.3, which="both", ls="--"); ax.legend(fontsize=9)
fig.savefig(f"figures/fedavot_feasible_alpha{ALPHA}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/fedavot_feasible_alpha{ALPHA}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/fedavot_feasible_alpha{ALPHA}_{ROUNDS}rounds.png")
