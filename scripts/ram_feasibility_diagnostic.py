# Why FedAVOT and FED-CVaR-AVG cannot be compared in the RAM setting of
# arXiv:2309.14176 ("Federated Learning Under Restricted User Availability") as published:
# their Random Access Model relays exactly ONE user's model per round
# (users_per_round = 1 in their script for Mnist.py; Algorithm 1 line 2 broadcasts the
# single RAM-selected user's (theta_i, t_i)).  With a batch of size 1 the FedAVOT
# transport has no degrees of freedom: the column-normalized weight of the only member
# is identically 1, so FedAVOT is *exactly* FedAvg-relay for ANY target p.
#
# This script quantifies that, and asks the natural follow-up: how many users per round
# does the RAM have to admit before the transport can actually deliver a uniform
# importance target p_i = 1/N?  Answer = the feasibility condition p_i <= pi_i from our
# paper, evaluated on THEIR availability distribution.
#
# No training here (that is ram_cvar_vs_fedavot.py); this is pure transport geometry.
#
# Side product: a subset-enumeration-free transport solver.  Masked IPFP converges to a
# product form Y[i,S] = u_i v_S 1{i in S}; column-normalizing gives the FedAVOT weight
#     w_i(S) = u_i / sum_{j in S} u_j,
# so the whole plan is determined by the N-vector u solving E_S[w_i(S) 1{i in S}] = p_i.
# We fit u by multiplicative updates over Monte-Carlo RAM draws, which removes the
# C(N,K) enumeration (and its coverage artifact) entirely.  Validated against the
# enumerated masked IPFP used by the other scripts (--validate).
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import sys

# ================================================================
# Config -- their MNIST setting (script for Mnist.py)
# ================================================================
NUM_USERS = 30                 # their K
N_RARE = 3                     # their k = int(K * 0.1); these hold digits 8,9 exclusively
RAM_SEED = 2517                # their user_probs = np.random.rand(K), normalized (they
                               # leave it unseeded); 2517 is the seed whose three
                               # smallest probabilities, 0.0061/0.0077/0.0107, match the
                               # 0.0053/0.0078/0.0107 tail quoted in their Table 1
RELAY_SIZES = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12]   # their users_per_round, generalized
MC_SUBSETS = 200_000           # RAM draws used to fit the transport
FIT_ITERS = 400
FIT_TOL = 1e-10
PI_SAMPLES = 500_000


# ================================================================
# Their RAM distribution
# ================================================================
def make_ram_probs(n, seed):
    """user_probs = np.random.rand(K) / sum, then the N_RARE least-available users are
    moved to the end of the list -- they are the ones holding the rare patterns.
    (Their published Mnist script moves the three LARGEST values instead, which
    contradicts the paper's Table 1 tail of 0.0107 / 0.0078 / 0.0053; we follow the
    paper.)"""
    rng = np.random.RandomState(seed)
    probs = rng.rand(n)
    probs = probs / probs.sum()
    order = np.argsort(probs)[::-1]        # descending: frequent users first
    return probs[order]                    # last N_RARE entries = least available


def inclusion_probs(r, n, k, samples, rng):
    """pi_i = P(user i is among the k relayed this round) under Gumbel top-k sampling."""
    if k >= n:
        return np.ones(n)
    incl = np.zeros(n)
    done = 0
    while done < samples:
        b = min(50_000, samples - done)
        g = rng.gumbel(size=(b, n)) + np.log(r)[None, :]
        tk = np.argpartition(-g, k, axis=1)[:, :k]
        np.add.at(incl, tk.ravel(), 1)
        done += b
    return incl / samples


def draw_subsets(r, n, k, samples, rng):
    """Monte-Carlo RAM draws: (samples, k) array of 0-based user indices."""
    out = np.empty((samples, k), dtype=np.int64)
    done = 0
    while done < samples:
        b = min(50_000, samples - done)
        g = rng.gumbel(size=(b, n)) + np.log(r)[None, :]
        out[done:done+b] = np.argpartition(-g, min(k, n-1), axis=1)[:, :k]
        done += b
    return out


# ================================================================
# Enumeration-free transport: fit u with w_i(S) = u_i / sum_{j in S} u_j
# ================================================================
def subset_weights(log_u, draws):
    """FedAVOT weights of every drawn subset: w_i(S) = softmax over S of log u."""
    ls = log_u[draws]
    ls = ls - ls.max(axis=1, keepdims=True)
    e = np.exp(ls)
    return e / e.sum(axis=1, keepdims=True)


def fit_transport(p, draws, n, iters=FIT_ITERS, tol=FIT_TOL):
    """Returns (log_u, p_hat, row_err). p_hat_i = E_S[w_i(S) 1{i in S}] is the achieved
    per-round expected weight of user i -- the surrogate marginal of Sec 3.3.

    Runs in log space: under infeasibility log u_i diverges for the starved users (that
    IS the stall), so any absolute floor on u silently flattens the plan and destroys
    the fit.  Recentring log u each step keeps the scale-invariant weights well posed."""
    m = draws.shape[0]
    flat = draws.ravel()
    log_p = np.log(p)
    log_u = np.zeros(n)
    p_hat = np.zeros(n)
    row_err, prev = np.inf, np.inf
    for _ in range(iters):
        w = subset_weights(log_u, draws)
        p_hat = np.bincount(flat, weights=w.ravel(), minlength=n) / m
        row_err = np.max(np.abs(p_hat - p))
        if row_err < tol or abs(prev - row_err) < 1e-15:
            break                                       # converged, or stalled (infeasible)
        prev = row_err
        log_u += log_p - np.log(np.maximum(p_hat, 1e-300))
        log_u -= log_u.mean()
    return log_u, p_hat, row_err


def validate_against_enumerated_ipfp(n=12, k=3, seed=1):
    """Cross-check the product-form solver against the enumerate-all-subsets masked IPFP
    used by the other scripts, on the same Monte-Carlo q.  Uses a FEASIBLE instance:
    when the problem is infeasible neither iteration has a fixed point and the two
    stalls need not coincide, so there would be nothing to compare."""
    rng = np.random.RandomState(seed)
    r = 0.5 + rng.rand(n); r /= r.sum()          # mild skew -> p_i = 1/n is feasible
    p = np.full(n, 1.0 / n)
    subsets = list(combinations(range(n), k))
    lookup = {s: i for i, s in enumerate(subsets)}
    draws = draw_subsets(r, n, k, 200_000, np.random.RandomState(7))
    srt = np.sort(draws, axis=1)
    code = srt @ (n ** np.arange(k - 1, -1, -1))                 # base-n key per subset
    key_of = np.full(n ** k, -1, dtype=np.int64)
    for s, j in lookup.items():
        key_of[int(np.dot(s, n ** np.arange(k - 1, -1, -1)))] = j
    counts = np.bincount(key_of[code], minlength=len(subsets)).astype(float)
    q = counts / counts.sum()

    # enumerated masked IPFP (same code path as scripts/imdbwiki_cvar_grid.py)
    M = np.zeros((n, len(subsets)), dtype=bool)
    for j, s in enumerate(subsets):
        for i in s:
            M[i, j] = True
    Y = np.where(M, q[None, :] / k, 0.0)
    for _ in range(20000):
        Y *= (p / np.maximum(Y.sum(axis=1), 1e-300))[:, None]
        Y *= (q / np.maximum(Y.sum(axis=0), 1e-300))[None, :]
        if np.max(np.abs(Y.sum(axis=1) - p)) < 1e-12:
            break
    T = np.zeros_like(Y)
    pos = q > 0
    T[:, pos] = Y[:, pos] / q[pos]

    # product form on the same draws
    log_u, p_hat, err = fit_transport(p, draws, n)
    T2 = np.zeros_like(T)
    for j, s in enumerate(subsets):
        us = np.exp(log_u[list(s)] - log_u[list(s)].max())
        T2[list(s), j] = us / us.sum()

    diff = np.max(np.abs(T[:, pos] - T2[:, pos]))
    print(f"[validate] N={n} K={k}: max |T_enumerated - T_productform| = {diff:.2e} "
          f"(row_err {err:.1e})")
    return diff


# ================================================================
# Main
# ================================================================
if "--validate" in sys.argv:
    validate_against_enumerated_ipfp()

r = make_ram_probs(NUM_USERS, RAM_SEED)
p = np.full(NUM_USERS, 1.0 / NUM_USERS)          # the fairness target: every user counts equally
rare = np.arange(NUM_USERS - N_RARE, NUM_USERS)  # the users holding digits 8,9 exclusively

print("=" * 78)
print("RAM setting of arXiv:2309.14176 (their MNIST script: K=30 users, "
      "3 rare users hold digits 8,9)")
print("=" * 78)
print(f"availability r: max {r.max():.4f}, median {np.median(r):.4f}, "
      f"3 rarest = {np.sort(r)[:3].round(4)}")
print(f"  (paper Table 1 quotes 0.0107 / 0.0078 / 0.0053 for the FashionMNIST run)")
print(f"target p: uniform, p_i = {p[0]:.4f} for all users")
print(f"rare users hold {p[rare].sum()*100:.1f}% of the target mass but "
      f"{r[rare].sum()*100:.2f}% of the availability mass\n")

rows = []
for R in RELAY_SIZES:
    pi = inclusion_probs(r, NUM_USERS, R, PI_SAMPLES, np.random.RandomState(0))
    draws = draw_subsets(r, NUM_USERS, R, MC_SUBSETS, np.random.RandomState(1))
    log_u, p_hat, err = fit_transport(p, draws, NUM_USERS)
    infeas = p > pi
    l1 = np.abs(p - p_hat).sum()
    rows.append(dict(R=R, pi=pi, p_hat=p_hat, err=err, infeas=infeas, l1=l1,
                     rare_pi=pi[rare].mean(), rare_phat=p_hat[rare].mean()))
    print(f"users/round R={R:2d} | infeasible users {infeas.sum():2d}/{NUM_USERS} "
          f"(target mass {p[infeas].sum()*100:5.1f}%) | IPFP row_err {err:.1e} | "
          f"||p - p_hat||_1 = {l1:.4f} | rare users: pi={pi[rare].mean():.4f} "
          f"achieved weight {p_hat[rare].mean():.4f} vs target {p[0]:.4f}")

print()
print("-" * 78)
r1 = rows[0]
assert RELAY_SIZES[0] == 1
print("R = 1 is the published setting.  Every batch is a singleton, so the FedAVOT")
print("weight of the only member is u_i/u_i = 1 identically: the transport is a no-op")
print(f"and FedAVOT == FedAvg-relay exactly.  The achieved marginal is r itself, so the")
print(f"realised importance is off by ||p - r||_1 = {np.abs(p - r).sum():.4f} "
      f"(rare users get {r[rare].mean():.4f} instead of {p[0]:.4f}, "
      f"{p[0]/r[rare].mean():.0f}x too little).")
print("Risk aversion (CVaR) is the only lever left, because it reweights ACROSS rounds")
print("(step-size amplification) rather than WITHIN a round (aggregation weights).")
first_feasible = next((d['R'] for d in rows if d['infeas'].sum() == 0), None)
if first_feasible:
    print(f"\nThe transport can only hit the uniform target once the RAM admits "
          f"R >= {first_feasible} users/round.")
else:
    print(f"\nThe target stays infeasible over the whole sweep (up to R="
          f"{RELAY_SIZES[-1]}): the rarest user has r={r.min():.4f}, so it needs "
          f"R ~ {int(np.ceil(1.0 / NUM_USERS / r.min()))} users/round before "
          f"pi_i reaches 1/N.")
print("-" * 78)

np.savez("data/ram_feasibility.npz",
         r=r, p=p, relay_sizes=np.array(RELAY_SIZES),
         pi=np.array([d['pi'] for d in rows]),
         p_hat=np.array([d['p_hat'] for d in rows]),
         row_err=np.array([d['err'] for d in rows]),
         l1=np.array([d['l1'] for d in rows]),
         n_infeasible=np.array([d['infeas'].sum() for d in rows]))

# ================================================================
# Figure
# ================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))

ax = axes[0]
idx = np.arange(NUM_USERS)
ax.bar(idx, r, color="tab:gray", label="availability $r$ (their RAM)")
ax.axhline(1.0 / NUM_USERS, color="tab:red", ls="--", lw=1.6,
           label="uniform target $p_i = 1/N$")
for i in rare:
    ax.patches[i].set_color("tab:orange")
ax.set_xlabel("user (sorted by availability)"); ax.set_ylabel("probability")
ax.set_title("Their RAM: 3 rare users (orange) hold\ndigits 8,9 exclusively")
ax.legend(fontsize=8); ax.grid(alpha=0.3, axis="y")

ax = axes[1]
for d, c in zip(rows, plt.cm.viridis(np.linspace(0, 0.9, len(rows)))):
    ax.plot(idx, d['pi'], color=c, lw=1.3, label=f"R={d['R']}")
ax.axhline(1.0 / NUM_USERS, color="tab:red", ls="--", lw=1.8, label="$p_i = 1/N$")
ax.set_yscale("log")
ax.set_xlabel("user"); ax.set_ylabel(r"inclusion probability $\pi_i$")
ax.set_title("Feasibility $p_i \\leq \\pi_i$ vs users relayed\nper round $R$")
ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)

ax = axes[2]
Rs = [d['R'] for d in rows]
ax.plot(Rs, [d['l1'] for d in rows], "o-", color="tab:blue", lw=1.8,
        label=r"$\|p - \hat{p}\|_1$ (transport shortfall)")
ax.plot(Rs, [d['infeas'].sum() / NUM_USERS for d in rows], "s-", color="tab:orange",
        lw=1.8, label="fraction of users infeasible")
if first_feasible:
    ax.axvline(first_feasible, color="tab:green", ls=":", lw=2,
               label=f"feasible at R={first_feasible}")
ax.axvline(1, color="tab:red", ls="--", lw=2, label="R=1 (published setting)")
ax.set_xlabel("users relayed per round $R$"); ax.set_ylabel("value")
ax.set_title("At R=1 the transport is a no-op:\nFedAVOT $\\equiv$ FedAvg")
ax.legend(fontsize=8); ax.grid(alpha=0.3)

fig.suptitle("FedAVOT in the restricted-availability (RAM) setting of arXiv:2309.14176",
             fontsize=13)
fig.tight_layout()
fig.savefig("figures/2026-07-27_ram_study/ram_feasibility_diagnostic.png", dpi=140, bbox_inches="tight")
fig.savefig("figures/2026-07-27_ram_study/ram_feasibility_diagnostic.pdf", bbox_inches="tight")
print("saved figures/2026-07-27_ram_study/ram_feasibility_diagnostic.png/.pdf and data/ram_feasibility.npz")
