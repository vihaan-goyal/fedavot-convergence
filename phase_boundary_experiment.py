# FedAVOT phase-boundary experiment -> final figure.
# Story: FedAVOT converges iff transport is feasible (p_i <= pi_i). Infeasibility bites
# only under availability-correlated distribution shift. Sweep skew alpha; show the boundary.
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ---------------- config ----------------
NUM_USERS, K = 50, 3
ROUNDS, EVAL_EVERY = 1500, 25
LOCAL_EPOCHS, DIM, SAMPLES_PER_USER = 5, 40, 30
LR = 1e-3
SEEDS = [0, 1, 2]
Q_SAMPLES = 400_000
IPFP_TOL, IPFP_MAX_ITERS = 1e-10, 3000
HET = 3.0                                   # strength of availability-correlated drift
ALPHAS = [0.5, 1.0, 1.5, 2.0, 3.0]
FEASIBLE_A, INFEASIBLE_A = 0.5, 3.0         # representative regimes for curve panels

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

# ---------------- one skew level ----------------
def run(alpha, keep_curves=False):
    p, r = make_skew(NUM_USERS, alpha)
    subsets = all_K_subsets(NUM_USERS, K)
    infeas = p[p > inclusion_probs(r, NUM_USERS, K, 200_000, np.random.RandomState(0))].sum()
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
        T, _ = solve_T(p, q, subsets); qc = np.cumsum(q)
        w_ot = np.zeros(DIM); w_k = np.zeros(DIM); w_f = np.zeros(DIM)
        c_ot, c_k, c_f = [], [], []
        for t in range(ROUNDS):
            j = int(np.searchsorted(qc, rng.rand()))
            users, wts = col_users_weights(T, subsets, j)
            w_ot = sum(a*local_train(*ud[u], w_ot.copy(), LOCAL_EPOCHS) for a, u in zip(wts, users))
            w_k  = sum((NUM_USERS/K)*p[u]*local_train(*ud[u], w_k.copy(), LOCAL_EPOCHS) for u in users)
            w_f  = sum(p[u]*local_train(*ud[u], w_f.copy(), LOCAL_EPOCHS) for u in range(NUM_USERS))
            if keep_curves and (t % EVAL_EVERY == 0):
                c_ot.append(global_loss(w_ot, ud, p)); c_k.append(global_loss(w_k, ud, p)); c_f.append(global_loss(w_f, ud, p))
        fin['ot'].append(global_loss(w_ot, ud, p)); fin['k'].append(global_loss(w_k, ud, p)); fin['f'].append(global_loss(w_f, ud, p))
        if keep_curves:
            curves['ot'].append(c_ot); curves['k'].append(c_k); curves['f'].append(c_f)
    out = {k: np.mean(v) for k, v in fin.items()}; out['infeas'] = infeas
    if keep_curves:
        out['curves'] = {k: np.mean(np.array(v), axis=0) for k, v in curves.items()}
    return out

# ---------------- run sweep ----------------
print("running sweep...")
results = {a: run(a, keep_curves=(a in (FEASIBLE_A, INFEASIBLE_A))) for a in ALPHAS}
for a in ALPHAS:
    R = results[a]
    print(f"alpha={a}: AVOT={R['ot']:.2f} full={R['f']:.2f} ratio={R['ot']/R['f']:.2f} infeas={R['infeas']:.2f}")

# ---------------- figure ----------------
BLUE, ORANGE, RED = "tab:blue", "tab:orange", "tab:red"
fig = plt.figure(figsize=(15, 5))
gs = gridspec.GridSpec(1, 3, wspace=0.28)

def plot_curves(ax, R, title):
    x = np.arange(len(R['curves']['ot']))*EVAL_EVERY
    ax.plot(x, R['curves']['ot'], color=BLUE, lw=2, label="FedAVOT")
    ax.plot(x, R['curves']['f'],  color=RED,  lw=2, label="FedAvg (full)")
    ax.plot(x, R['curves']['k'],  color=ORANGE, lw=1.3, alpha=0.8, label="FedAvg (K)")
    ax.set_yscale("log"); ax.set_xlabel("Round"); ax.set_ylabel("Global p-weighted MSE (log)")
    ax.set_title(title); ax.grid(alpha=0.3, which="both", ls="--"); ax.legend(fontsize=9)

plot_curves(fig.add_subplot(gs[0]), results[FEASIBLE_A],
            f"Feasible regime (α={FEASIBLE_A}, {results[FEASIBLE_A]['infeas']*100:.0f}% infeasible)\nFedAVOT converges to optimum")
plot_curves(fig.add_subplot(gs[1]), results[INFEASIBLE_A],
            f"Infeasible regime (α={INFEASIBLE_A}, {results[INFEASIBLE_A]['infeas']*100:.0f}% infeasible)\nFedAVOT stalls far above optimum")

ax = fig.add_subplot(gs[2])
infeas = [results[a]['infeas']*100 for a in ALPHAS]
ax.plot(infeas, [results[a]['ot'] for a in ALPHAS], 'o-', color=BLUE, lw=2, label="FedAVOT")
ax.plot(infeas, [results[a]['f']  for a in ALPHAS], 's-', color=RED,  lw=2, label="FedAvg (full)")
ax.set_yscale("log"); ax.set_xlabel("% of importance mass that is infeasible ($p_i>\\pi_i$)")
ax.set_ylabel("Final global p-weighted MSE (log)")
ax.set_title("Phase boundary\nfinal loss vs transport infeasibility")
ax.grid(alpha=0.3, which="both", ls="--"); ax.legend(fontsize=9)
for a, xi in zip(ALPHAS, infeas):
    ax.annotate(f"{results[a]['ot']/results[a]['f']:.1f}×",
                (xi, results[a]['ot']), textcoords="offset points", xytext=(4, 5), fontsize=8, color=BLUE)

fig.suptitle("FedAVOT converges only when the p↔availability transport is feasible", fontsize=13, y=1.02)
fig.savefig("fedavot_phase_boundary.png", dpi=140, bbox_inches="tight")
print("saved fedavot_phase_boundary.png")
