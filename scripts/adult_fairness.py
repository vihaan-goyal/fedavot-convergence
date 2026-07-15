# Adult (Census Income) fairness experiment for the OT-SGD paper (Problem 1 of the
# 2026-07-15 complete.tex review: the paper promises Adult fairness results but has none).
#
# Design (new, replaces Amtej's uncommitted Oct-2025 pipeline; needs Herlock's sign-off):
# clients are GROUP-HOMOGENEOUS (each holds data from exactly one race group, users per
# group proportional to prevalence), the target importance p is UNIFORM ACROSS GROUPS
# (each race group gets 1/5 of the objective -- that is the fairness statement), and the
# two availability regimes bracket the feasibility condition exactly like IMDb-Wiki:
#
#   PREVALENCE regime: every client equally available (r uniform), i.e. participation
#     mirrors data prevalence -- the realistic FL default. Minority-group clients then
#     have inclusion probability pi_i ~= K/N far below their importance p_i, so the
#     transport is INFEASIBLE (expected: 5/100 users holding ~60% of importance mass).
#   ALIGNED regime: availability proportional to importance (r ~ p), so pi_i ~= K*p_i
#     > p_i for everyone -> FEASIBLE.
#
# Headline the design buys: "even with every client equally available, a group-uniform
# fairness target is infeasible when group sizes are imbalanced."
#
# Task: binary logistic regression, income > 50K, one-hot + standardized features.
# Everything else (Gumbel top-K sampling, MC q, masked IPFP, same-draw parallel updates,
# tail-500 stats) follows the common protocol of the IMDb-Wiki scripts.
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
ROUNDS = 2000
LOCAL_EPOCHS = 5
SAMPLES_PER_USER = 30
LR = 0.1
SEEDS = [0, 1, 2, 3, 4]
NUM_SAMPLES_FOR_Q = 1_000_000
GROUP_COL = "race"              # sensitive attribute defining the groups

IPFP_TOL = 1e-12
IPFP_MAX_ITERS = 1000
TAIL = 500                      # rounds averaged for the quotable final numbers
K_CAP = 1e12                    # freeze FedAvg(K) at this loss once it diverges

# ================================================================
# Masked IPFP utilities (same as the IMDb-Wiki scripts)
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

def all_K_subsets_1based(N, K):
    return list(combinations(range(1, N+1), K))

def estimate_q(subsets, r, N, K, samples, rng):
    lookup = {s: i for i, s in enumerate(subsets)}
    counts = np.zeros(len(subsets))
    logr = np.log(r)
    done = 0
    while done < samples:
        b = min(200_000, samples - done)
        g = rng.gumbel(size=(b, N)) + logr[None, :]
        tk = np.argpartition(-g, K, axis=1)[:, :K]
        tk.sort(axis=1)
        uniq, cnt = np.unique(tk + 1, axis=0, return_counts=True)
        for row, c in zip(uniq, cnt):
            counts[lookup[tuple(row.tolist())]] += c
        done += b
    return counts / counts.sum()

def inclusion_probs(r, N, K, samples, rng):
    g = rng.gumbel(size=(samples, N)) + np.log(r)[None, :]
    tk = np.argpartition(-g, K, axis=1)[:, :K]
    incl = np.zeros(N)
    np.add.at(incl, tk.ravel(), 1)
    return incl / samples

# ================================================================
# Vectorized logistic-regression helpers (binary CE, batched over users)
# ================================================================
def batched_local_train(Xs, ys, w, epochs):
    W = np.repeat(w[None, :], Xs.shape[0], axis=0)
    for _ in range(epochs):
        z = np.einsum('msd,md->ms', Xs, W)
        sig = 1.0 / (1.0 + np.exp(-z))
        grad = np.einsum('msd,ms->md', Xs, sig - ys) / ys.shape[1]
        W = W - LR * grad
    return W

def per_user_losses(w, X_all, y_all):
    z = np.einsum('nsd,d->ns', X_all, w)
    return (np.logaddexp(0.0, z) - y_all * z).mean(axis=1)   # CE per user

# ================================================================
# Data: group-homogeneous clients from Adult
# ================================================================
df = pd.read_csv("data/adult.csv")
y_bin = (df["class"].str.strip() == ">50K").astype(float).values

num_cols = ["age", "fnlwgt", "education-num", "capital-gain", "capital-loss",
            "hours-per-week"]
cat_cols = ["workclass", "education", "marital-status", "occupation",
            "relationship", "race", "sex", "native-country"]
Xnum = df[num_cols].astype(float).values
Xnum = (Xnum - Xnum.mean(axis=0)) / np.maximum(Xnum.std(axis=0), 1e-9)
Xcat = pd.get_dummies(df[cat_cols].fillna("Unknown"), dtype=float).values
X_feat = np.concatenate([Xnum, Xcat, np.ones((len(df), 1))], axis=1)  # +intercept
DIM = X_feat.shape[1]

groups_series = df[GROUP_COL].str.strip()
GROUP_NAMES = sorted(groups_series.unique(), key=lambda g: -(groups_series == g).sum())
NG = len(GROUP_NAMES)
counts = np.array([(groups_series == g).sum() for g in GROUP_NAMES], dtype=float)
print(f"DIM = {DIM}; groups: " + ", ".join(f"{g} {int(c)}" for g, c in zip(GROUP_NAMES, counts)))

# users per group: proportional to prevalence, at least 1, forced to sum to NUM_USERS
users_per_group = np.maximum(1, np.round(counts / counts.sum() * NUM_USERS)).astype(int)
users_per_group[0] += NUM_USERS - users_per_group.sum()   # absorb rounding in majority
assert users_per_group.sum() == NUM_USERS
print("users per group:", dict(zip(GROUP_NAMES, users_per_group)))

# fixed partition (data identical across seeds; only the subset draws vary, as in the
# IMDb-Wiki scripts)
rng_part = np.random.RandomState(42)
X_users, y_users, group_of_user = [], [], []
for gi, g in enumerate(GROUP_NAMES):
    idx = np.where(groups_series.values == g)[0]
    rng_part.shuffle(idx)
    need = users_per_group[gi] * SAMPLES_PER_USER
    assert len(idx) >= need, f"group {g} too small: {len(idx)} < {need}"
    take = idx[:need].reshape(users_per_group[gi], SAMPLES_PER_USER)
    for rows in take:
        X_users.append(X_feat[rows]); y_users.append(y_bin[rows]); group_of_user.append(gi)
X_all = np.stack(X_users)                  # (N, S, DIM)
y_all = np.stack(y_users)                  # (N, S)
group_of_user = np.array(group_of_user)
group_slices = [np.where(group_of_user == gi)[0] for gi in range(NG)]

# importance p: uniform across groups (the fairness target), equal within group
p = np.zeros(NUM_USERS)
for gi in range(NG):
    p[group_slices[gi]] = (1.0 / NG) / users_per_group[gi]
assert abs(p.sum() - 1) < 1e-12

# availability r per regime
REGIMES = {
    "prevalence": np.ones(NUM_USERS) / NUM_USERS,        # uniform clients ~ prevalence
    "aligned":    p.copy(),                              # availability tracks importance
}

# ================================================================
# Transport per regime, then training
# ================================================================
subsets = all_K_subsets_1based(NUM_USERS, K)
results = {}
for regime, r in REGIMES.items():
    print(f"\n=== regime: {regime} ===")
    pi = inclusion_probs(r, NUM_USERS, K, 500_000, np.random.RandomState(0))
    infeas = p > pi
    print(f"infeasible users: {infeas.sum()}/{NUM_USERS}, "
          f"infeasible p-mass = {p[infeas].sum()*100:.1f}%, "
          f"max p_i/pi_i = {np.max(p/np.maximum(pi, 1e-12)):.2f}")

    t0 = time.time()
    q = estimate_q(subsets, r, NUM_USERS, K, NUM_SAMPLES_FOR_Q, np.random.RandomState(0))
    q = (q + 1e-12) / q.sum()
    print(f"estimate_q done in {time.time()-t0:.0f}s")
    T = solve_T(p, q, subsets)
    q_cum = np.cumsum(q)

    F = {m: [] for m in ("avot", "faK", "full")}         # objective curves per seed
    G = {m: [] for m in ("avot", "faK", "full")}         # per-group CE curves per seed
    for seed in SEEDS:
        t0 = time.time()
        rng = np.random.RandomState(seed)
        w = {m: np.zeros(DIM) for m in ("avot", "faK", "full")}
        Fs = {m: [] for m in F}; Gs = {m: [] for m in G}
        k_diverged = False
        for _ in range(ROUNDS):
            j = np.searchsorted(q_cum, rng.rand())
            users, weights = column_users_and_weights(T, subsets, j)

            w["avot"] = weights @ batched_local_train(X_all[users], y_all[users],
                                                      w["avot"], LOCAL_EPOCHS)
            if not k_diverged:
                Mk = batched_local_train(X_all[users], y_all[users], w["faK"], LOCAL_EPOCHS)
                w["faK"] = (NUM_USERS / K) * (p[users] @ Mk)
                if not np.all(np.isfinite(w["faK"])):
                    k_diverged = True
            w["full"] = p @ batched_local_train(X_all, y_all, w["full"], LOCAL_EPOCHS)

            for m in F:
                if m == "faK" and k_diverged:
                    Fs[m].append(K_CAP); Gs[m].append([K_CAP]*NG); continue
                ul = per_user_losses(w[m], X_all, y_all)
                f = p @ ul
                if m == "faK" and (not np.isfinite(f) or f > K_CAP):
                    k_diverged = True
                    Fs[m].append(K_CAP); Gs[m].append([K_CAP]*NG); continue
                Fs[m].append(f)
                Gs[m].append([ul[s].mean() for s in group_slices])
        for m in F:
            F[m].append(np.array(Fs[m])); G[m].append(np.array(Gs[m]))
        print(f"seed {seed}: {time.time()-t0:.0f}s, tail-{TAIL} CE "
              + " ".join(f"{m}={np.mean(Fs[m][-TAIL:]):.4f}" for m in F))

    results[regime] = {"F": {m: np.array(F[m]) for m in F},
                       "G": {m: np.array(G[m]) for m in G},
                       "r": r, "pi": pi, "infeas": infeas}

# ================================================================
# Summary numbers
# ================================================================
def tail_stats(A):                        # A: (seeds, ROUNDS)
    per_seed = A[:, -TAIL:].mean(axis=1)
    return per_seed.mean(), per_seed.std()

print("\n================ FINAL (tail-%d over %d seeds) ================" % (TAIL, len(SEEDS)))
for regime, res in results.items():
    print(f"\n--- {regime} ---")
    for m, label in (("avot", "FedAVOT"), ("faK", "FedAvg(K)"), ("full", "FedAvg(full)")):
        mu, sd = tail_stats(res["F"][m])
        gtail = res["G"][m][:, -TAIL:, :].mean(axis=(0, 1))   # (NG,)
        gap = gtail.max() - gtail.min()
        gstr = " ".join(f"{n.split('-')[0]}={v:.3f}" for n, v in zip(GROUP_NAMES, gtail))
        print(f"{label:13s} F = {mu:.4f} ± {sd:.4f} | group CE: {gstr} | gap = {gap:.3f}")

# ================================================================
# Save curves + figure
# ================================================================
np.savez(f"data/adult_{GROUP_COL}_K{K}_{ROUNDS}rounds_curves.npz",
         **{f"{regime}_{m}_F": res["F"][m] for regime, res in results.items() for m in res["F"]},
         **{f"{regime}_{m}_G": res["G"][m] for regime, res in results.items() for m in res["G"]},
         **{f"{regime}_r": res["r"] for regime, res in results.items()},
         **{f"{regime}_pi": res["pi"] for regime, res in results.items()},
         p=p, group_names=np.array(GROUP_NAMES), users_per_group=users_per_group)

COL = {"avot": "tab:blue", "faK": "tab:orange", "full": "tab:red"}
LBL = {"avot": f"FedAVOT (K={K})", "faK": f"FedAvg (K={K})", "full": "FedAvg (full)"}
TITLES = {"prevalence": f"Prevalence availability (uniform clients) — INFEASIBLE",
          "aligned": f"Importance-aligned availability — FEASIBLE"}

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
for col, (regime, res) in enumerate(results.items()):
    k_diverged = bool(res["F"]["faK"].max() >= K_CAP)

    # --- top row: full trajectories on a log axis (keeps FedAvg(K)'s instability
    # visible without letting its spikes squash FedAVOT vs full), plus a linear
    # inset zoomed on the second half where blue vs red is the actual comparison.
    ax = axes[0, col]
    for m in ("avot", "faK", "full"):
        if m == "faK" and k_diverged:
            continue
        A = res["F"][m]
        mean, std = A.mean(axis=0), A.std(axis=0)
        ax.plot(mean, color=COL[m], label=LBL[m], lw=1.3)
        if m != "faK":
            ax.fill_between(np.arange(len(mean)), mean-std, mean+std, color=COL[m], alpha=0.15)
    ax.set_yscale("log")
    ax.set_ylim(0.18, 3.0)
    if k_diverged:
        ax.annotate("FedAvg(K) diverges:\nfixed N/K scaling assumes\nuniform participation",
                    xy=(0.03, 0.35), xycoords="axes fraction", va="top",
                    fontsize=9, color="tab:orange")
    ax.set_xlabel("Round"); ax.set_ylabel(r"Objective $F(\theta)$ (group-uniform CE, log)")
    ax.set_title(TITLES[regime], fontsize=11)
    ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3, which="both")

    t0 = ROUNDS // 2
    axi = ax.inset_axes([0.42, 0.48, 0.55, 0.38])
    for m in ("avot", "full"):
        A = res["F"][m]
        mean, std = A.mean(axis=0)[t0:], A.std(axis=0)[t0:]
        xz = np.arange(t0, ROUNDS)
        axi.plot(xz, mean, color=COL[m], lw=1.2)
        axi.fill_between(xz, mean-std, mean+std, color=COL[m], alpha=0.15)
    axi.set_title(f"zoom: FedAVOT vs full, rounds {t0}–{ROUNDS} (linear)", fontsize=8)
    axi.tick_params(labelsize=7)
    axi.grid(alpha=0.3)

    ax = axes[1, col]
    xs = np.arange(NG); wd = 0.26
    methods = ("avot", "full") if k_diverged else ("avot", "faK", "full")
    offs = {2: (-0.5, 0.5), 3: (-1, 0, 1)}[len(methods)]
    for k, m in enumerate(methods):
        gtail = res["G"][m][:, -TAIL:, :].mean(axis=(0, 1))
        ax.bar(xs + offs[k]*wd, gtail, wd, color=COL[m], label=LBL[m])
    if k_diverged:
        ax.annotate("FedAvg(K) diverged (omitted)", xy=(0.03, 0.96),
                    xycoords="axes fraction", va="top", fontsize=9, color="tab:orange")
    ax.set_ylim(0, 1.25 * max(res["G"][m][:, -TAIL:, :].mean(axis=(0, 1)).max()
                              for m in methods))
    ax.set_xticks(xs)
    ax.set_xticklabels([g.replace("-", "-\n") for g in GROUP_NAMES], fontsize=8)
    ax.set_ylabel(f"Final per-group CE (tail-{TAIL})")
    ax.set_title(f"Per-race CE, {regime} regime", fontsize=11)
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)

fig.suptitle(f"Adult income classification, group-uniform importance over {GROUP_COL} "
             f"(N={NUM_USERS}, K={K}, {ROUNDS} rounds, {len(SEEDS)} seeds)", fontsize=12)
fig.tight_layout()
fig.savefig(f"figures/adult_{GROUP_COL}_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/adult_{GROUP_COL}_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"\nsaved figures/adult_{GROUP_COL}_K{K}_{ROUNDS}rounds.png/.pdf")
