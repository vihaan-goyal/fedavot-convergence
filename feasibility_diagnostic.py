# FedAVOT mechanism figure -> the "smoking gun" for Herlock's question.
# Claim: FedAVOT does not fail because of a bug in the update rule. It fails because IPFP is
# asked to solve an INFEASIBLE transport problem: the achieved marginal m_i = sum_j q_j T[i,j]
# is capped at the inclusion probability pi_i, so whenever p_i > pi_i the debiasing silently
# cannot deliver the weight the objective demands. This script makes that gap visible.
#
# No training loop here -- everything is a property of (p, r, q, T). Fast.
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ---------------- config (matches phase_boundary_experiment.py) ----------------
NUM_USERS, K = 50, 3
Q_SAMPLES = 300_000
PI_SAMPLES = 300_000
IPFP_TOL, IPFP_MAX_ITERS = 1e-10, 3000
FEASIBLE_A, INFEASIBLE_A = 0.2, 3.0    # 0.2 -> every p_i <= pi_i (genuinely feasible); 3.0 -> 87% infeasible
SEED = 0

# ---------------- transport (with IPFP row-error trajectory) ----------------
def build_mask(n, subsets):
    M = np.zeros((n, len(subsets)), dtype=bool)
    for j, s in enumerate(subsets):
        for i in s: M[i-1, j] = True
    return M

def ipfp_masked(p, q, M, tol, max_iter):
    """Masked IPFP; also returns the per-iteration row-marginal error history."""
    Y = np.zeros_like(M, dtype=float)
    for j in range(M.shape[1]):
        rows = np.where(M[:, j])[0]
        if rows.size: Y[rows, j] = q[j] / rows.size
    hist = []
    for _ in range(max_iter):
        Y *= (p / np.maximum(Y.sum(1), 1e-12))[:, None]
        Y *= (q / np.maximum(Y.sum(0), 1e-12))[None, :]
        row_err = np.max(np.abs(Y.sum(1) - p))
        hist.append(row_err)
        if row_err < tol: break
    return Y, np.array(hist)

def solve_T(p, q, subsets):
    M = build_mask(len(p), subsets)
    Y, hist = ipfp_masked(p, q, M, IPFP_TOL, IPFP_MAX_ITERS)
    T = np.zeros_like(Y); pos = q > 0
    T[:, pos] = Y[:, pos] / q[pos]; T[~M] = 0
    s = T.sum(0, keepdims=True); s[s == 0] = 1.0; T /= s
    return T, hist

# ---------------- distributions ----------------
def make_skew(N, a):
    idx = np.arange(1, N+1, dtype=float)
    r = idx**a; p = idx[::-1]**a
    return p/p.sum(), r/r.sum()
def all_K_subsets(N, K): return list(combinations(range(1, N+1), K))

def estimate_q(subsets, r, N, K, samples, rng):    # Gumbel top-K, sampling ~ r without replacement
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

# ---------------- analyze one regime ----------------
def analyze(alpha):
    rng = np.random.RandomState(SEED)
    p, r = make_skew(NUM_USERS, alpha)
    subsets = all_K_subsets(NUM_USERS, K)
    pi = inclusion_probs(r, NUM_USERS, K, PI_SAMPLES, rng)
    q = estimate_q(subsets, r, NUM_USERS, K, Q_SAMPLES, rng); q = q + 1e-12; q /= q.sum()
    T, hist = solve_T(p, q, subsets)
    m = T @ q                                   # achieved marginal delivered to each client
    infeasible = p > pi                         # coverage condition p_i <= pi_i violated
    missing = np.maximum(0.0, p - m)            # p-weight IPFP cannot deliver
    return dict(alpha=alpha, p=p, pi=pi, m=m, infeasible=infeasible,
                infeas_mass=p[infeasible].sum(), missing_mass=missing.sum(),
                final_row_err=hist[-1], hist=hist, iters=len(hist))

print("solving feasible regime...");   F = analyze(FEASIBLE_A)
print("solving infeasible regime..."); I = analyze(INFEASIBLE_A)
for tag, R in [("feasible", F), ("infeasible", I)]:
    print(f"[{tag}] alpha={R['alpha']}  infeasible clients={int(R['infeasible'].sum())}/{NUM_USERS}  "
          f"infeasible p-mass={R['infeas_mass']*100:.0f}%  undelivered p-mass={R['missing_mass']*100:.1f}%  "
          f"IPFP iters={R['iters']}  final row_err={R['final_row_err']:.2e}")

# ---------------- figure ----------------
BLUE, RED, GRAY = "tab:blue", "tab:red", "0.55"
fig = plt.figure(figsize=(13, 8.5))
gs = gridspec.GridSpec(2, 2, hspace=0.32, wspace=0.24)

def scatter_panel(ax, R, title):
    p, pi, m, inf = R['p'], R['pi'], R['m'], R['infeasible']
    lo = max(min(p.min(), m.min(), pi.min()) * 0.5, 1e-8)
    hi = max(p.max(), pi.max()) * 2.0
    ax.plot([lo, hi], [lo, hi], color=GRAY, ls="--", lw=1.2, zorder=1,
            label="perfect debiasing ($m_i=p_i$)")
    # feasibility ceiling pi_i vs p_i (grey), then achieved m_i vs p_i (blue/red)
    ax.scatter(p, pi, s=16, facecolors="none", edgecolors=GRAY, lw=0.9, zorder=2,
               label=r"ceiling $\pi_i$ (max deliverable)")
    ax.scatter(p[~inf], m[~inf], s=26, color=BLUE, zorder=3, label="feasible client")
    ax.scatter(p[inf],  m[inf],  s=30, color=RED,  marker="X", zorder=4, label="infeasible client")
    # draw the shortfall as a vertical drop from the diagonal to the achieved point
    for i in np.where(inf)[0]:
        ax.plot([p[i], p[i]], [m[i], p[i]], color=RED, lw=0.8, alpha=0.5, zorder=2)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel(r"target importance $p_i$")
    ax.set_ylabel(r"achieved weight $m_i=\sum_j q_j\,T[i,j]$")
    ax.set_title(title); ax.grid(alpha=0.3, which="both", ls=":"); ax.legend(fontsize=8, loc="upper left")

def err_panel(ax, R, title):
    ax.plot(np.arange(1, R['iters']+1), R['hist'], color=RED if R['infeasible'].sum() else BLUE, lw=1.8)
    ax.set_yscale("log"); ax.set_xlabel("IPFP iteration")
    ax.set_ylabel(r"row-marginal error $\max_i|\sum_j Y_{ij}-p_i|$")
    ax.set_title(title); ax.grid(alpha=0.3, which="both", ls=":")
    ax.axhline(IPFP_TOL, color=GRAY, ls="--", lw=1, label=f"tol={IPFP_TOL:g}")
    ax.legend(fontsize=8, loc="upper right")

scatter_panel(fig.add_subplot(gs[0, 0]), F,
              f"Feasible ($\\alpha$={F['alpha']}): IPFP hits the target\n"
              f"{F['missing_mass']*100:.1f}% of $p$-mass undelivered")
scatter_panel(fig.add_subplot(gs[0, 1]), I,
              f"Infeasible ($\\alpha$={I['alpha']}): high-$p$ clients pinned at ceiling\n"
              f"{I['missing_mass']*100:.0f}% of $p$-mass undelivered $\\Rightarrow$ loss floor")
F_conv = F['final_row_err'] < 1e-8
err_panel(fig.add_subplot(gs[1, 0]), F,
          (f"Feasible: IPFP matches $p$ (row_err$\\to${F['final_row_err']:.0e} in {F['iters']} iters)"
           if F_conv else
           f"Feasible: row_err$\\to${F['final_row_err']:.1e} in {F['iters']} iters"))
err_panel(fig.add_subplot(gs[1, 1]), I,
          f"Infeasible: IPFP never matches $p$, stalls at {I['final_row_err']:.1e} (max_iters={I['iters']})")

fig.suptitle(r"Why FedAVOT stalls: transport is infeasible ($p_i>\pi_i$), so IPFP debiasing silently fails",
             fontsize=13, y=0.98)
fig.savefig("fedavot_mechanism.png", dpi=140, bbox_inches="tight")
fig.savefig("fedavot_mechanism.pdf", bbox_inches="tight")
print("saved fedavot_mechanism.png / .pdf")
