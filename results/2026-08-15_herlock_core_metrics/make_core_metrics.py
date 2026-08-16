# Herlock core-metrics deliverable (2026-08-15): Tier 1-3 figures + CSVs and the
# bonus per-client-over-time heatmaps, all recomputed from the completed sweep at
# results/2026-08-10_main_sweep/ (no retraining). Tail-500 = mean over the last
# 500 logged rounds (3500-3999), computed per seed first, then mean +- std across
# the 5 seeds. CVaR algorithms use the per-cell min-max-winning (alpha, gamma).
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "results/2026-08-10_main_sweep/"
OUT = "results/2026-08-15_herlock_core_metrics/"
os.makedirs(OUT, exist_ok=True)
TAIL, NSEED, NUSER = 500, 5, 100

CELLS = [("adult", "feasible"), ("adult", "infeasible"),
         ("imdbwiki", "feasible"), ("imdbwiki", "infeasible")]
# per-cell tuned (min-max-winning) configs; imdbwiki infeasible = best genuine
# CVaR cell (alpha<1, gamma<1), which sits ~= its own baseline by construction
CFG = {
    ("adult", "feasible", "fedavot_cvar"): (0.1, 0.4),
    ("adult", "feasible", "fedcvar"): (0.1, 0.4),
    ("adult", "infeasible", "fedavot_cvar"): (0.2, 0.8),
    ("adult", "infeasible", "fedcvar"): (0.1, 0.7),
    ("imdbwiki", "feasible", "fedavot_cvar"): (0.9, 0.2),
    ("imdbwiki", "feasible", "fedcvar"): (0.4, 0.8),
    ("imdbwiki", "infeasible", "fedavot_cvar"): (0.9, 0.9),
    ("imdbwiki", "infeasible", "fedcvar"): (0.9, 0.9),
}
# repo plot conventions: FedAVOT blue, FedAvg(K) orange, full red,
# CVaR-combination green, CVaR-uniform purple
ALGS = [
    ("fedavot", "FedAVOT", "#1f77b4"),
    ("fedavg", "FedAvg (unif-K)", "#ff7f0e"),
    ("fedavot_cvar", "FedAVOT+CVaR", "#2ca02c"),
    ("fedcvar", "FedCVaR", "#9467bd"),
    ("full", "FedAvg (full)", "#d62728"),
]
GCOLS = {
    "adult": ["group_White", "group_Black", "group_Asian-Pac-Islander",
              "group_Amer-Indian-Eskimo", "group_Other"],
    "imdbwiki": ["group_tier1", "group_tier2", "group_tier3", "group_tier4",
                 "group_tier5"],
}
UCOLS = [f"user_{i}" for i in range(NUSER)]


def cfg_label(ds, rg, model, name):
    if model in ("fedavot_cvar", "fedcvar"):
        a, g = CFG[(ds, rg, model)]
        return f"{name}\n($\\alpha$={a:.1f}, $\\gamma$={g:.1f})"
    return name


def fname(ds, rg, model, seed):
    if model in ("fedavot_cvar", "fedcvar"):
        a, g = CFG[(ds, rg, model)]
        return f"{D}{ds}_{rg}_{model}_a{a:.2f}_g{g:.2f}_seed{seed}.csv.gz"
    return f"{D}{ds}_{rg}_{model}_seed{seed}.csv.gz"


# ---- load tails: users[(ds,rg)][model] -> (seed, 100), groups -> (seed, 5) ----
users, groups = {}, {}
for ds, rg in CELLS:
    users[(ds, rg)], groups[(ds, rg)] = {}, {}
    for model, _, _ in ALGS:
        u = np.empty((NSEED, NUSER))
        g = np.empty((NSEED, 5))
        for s in range(NSEED):
            df = pd.read_csv(fname(ds, rg, model, s),
                             usecols=UCOLS + GCOLS[ds]).tail(TAIL)
            u[s] = df[UCOLS].mean().values
            g[s] = df[GCOLS[ds]].mean().values
        users[(ds, rg)][model] = u
        groups[(ds, rg)][model] = g
    print(f"loaded {ds} {rg}")

# ---------------------------- Tier 1: overall ---------------------------------
rows = []
for ds, rg in CELLS:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for x, (model, name, col) in enumerate(ALGS):
        per_seed = users[(ds, rg)][model].mean(axis=1)  # unweighted client mean
        m, sd = per_seed.mean(), per_seed.std(ddof=1)
        ax.errorbar(x, m, yerr=sd, fmt="o", color=col, ms=8, capsize=5,
                    lw=1.8, capthick=1.8)
        rows.append(dict(algorithm=name, dataset=ds, regime=rg, mean=m, std=sd))
    ax.set_xticks(range(5))
    ax.set_xticklabels([cfg_label(ds, rg, m, n) for m, n, _ in ALGS],
                       fontsize=8.5)
    ax.set_ylabel("tail-500 loss (mean over 100 clients)")
    ax.set_title(f"{ds} / {rg} — overall tail-500 loss (mean ± std, 5 seeds)")
    ax.margins(y=0.15)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}tier1_overall_{ds}_{rg}.{ext}", dpi=150)
    plt.close(fig)
pd.DataFrame(rows).to_csv(OUT + "tier1_overall.csv", index=False,
                          float_format="%.6g")

# ------------------------ Tier 2: sorted client curves ------------------------
rows = []
for ds, rg in CELLS:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    curves = {}
    for model, name, col in ALGS:
        u = users[(ds, rg)][model]                 # (seed, 100)
        seedmean = u.mean(axis=0)                  # (100,)
        curves[model] = seedmean
        # dash the CVaR variants: at near-degenerate tuned configs they coincide
        # with their own baselines and would otherwise hide them entirely
        ls = (0, (4, 2)) if model in ("fedavot_cvar", "fedcvar") else "-"
        ax.plot(np.arange(1, NUSER + 1), np.sort(seedmean), color=col, lw=2,
                linestyle=ls,
                label=cfg_label(ds, rg, model, name).replace("\n", " "))
        worst10 = np.argsort(seedmean)[-10:]       # fixed identity across seeds
        w10 = u[:, worst10].mean(axis=1)           # per-seed worst-10 mean
        rows.append(dict(algorithm=name, dataset=ds, regime=rg,
                         worst10_mean=w10.mean(), worst10_std=w10.std(ddof=1),
                         max_client_loss=seedmean.max()))
    allv = np.concatenate(list(curves.values()))
    if allv.max() / max(allv.min(), 1e-12) > 50:
        ax.set_yscale("log")
    ax.set_xlabel("client rank (sorted ascending per algorithm)")
    ax.set_ylabel("tail-500 loss (seed-mean, per client)")
    ax.set_title(f"{ds} / {rg} — sorted per-client tail-500 loss")
    ax.legend(fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}tier2_perclient_{ds}_{rg}.{ext}", dpi=150)
    plt.close(fig)
pd.DataFrame(rows).to_csv(OUT + "tier2_worst_clients.csv", index=False,
                          float_format="%.6g")

# ------------------------- Tier 3: group regret heatmap -----------------------
rows = []
for ds, rg in CELLS:
    full_g = groups[(ds, rg)]["full"]              # (seed, 5); identical seeds
    R = np.empty((5, 5))                           # rows=groups, cols=algs
    for x, (model, name, _) in enumerate(ALGS):
        reg = groups[(ds, rg)][model] - full_g     # per-seed regret (seed, 5)
        R[:, x] = reg.mean(axis=0)
        for gi, gc in enumerate(GCOLS[ds]):
            rows.append(dict(algorithm=name, dataset=ds, regime=rg,
                             group=gc.replace("group_", ""),
                             regret_mean=reg.mean(axis=0)[gi],
                             regret_std=reg.std(axis=0, ddof=1)[gi]))
    vmax = np.abs(R).max()
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    im = ax.imshow(R, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    fmt = "%+.3f" if ds == "adult" else "%+.1f"
    for gi in range(5):
        for x in range(5):
            dark = abs(R[gi, x]) > 0.6 * vmax
            ax.text(x, gi, fmt % R[gi, x], ha="center", va="center",
                    fontsize=9, color="white" if dark else "black")
    ax.set_xticks(range(5))
    ax.set_xticklabels([cfg_label(ds, rg, m, n) for m, n, _ in ALGS],
                       fontsize=7.5)
    ax.set_yticks(range(5))
    ax.set_yticklabels([c.replace("group_", "") for c in GCOLS[ds]], fontsize=9)
    ax.set_title(f"{ds} / {rg} — per-group regret vs FedAvg(full), tail-500")
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("regret = method − full  (blue: beats full)")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}tier3_groupregret_{ds}_{rg}.{ext}", dpi=150)
    plt.close(fig)
pd.DataFrame(rows).to_csv(OUT + "tier3_group_regret.csv", index=False,
                          float_format="%.6g")

# -------- Bonus: adult per-client-over-time heatmaps (seed-averaged) ----------
BLOCKS = [("White", 0, 85), ("Black", 85, 95), ("Asian-Pac", 95, 98),
          ("Amer-Ind", 98, 99), ("Other", 99, 100)]
NAMES = {m: n for m, n, _ in ALGS}
mats = {}
for rg in ("feasible", "infeasible"):
    for model in ("fedavot", "fedavot_cvar"):
        acc = np.zeros((4000, NUSER))
        for s in range(NSEED):
            acc += pd.read_csv(fname("adult", rg, model, s),
                               usecols=UCOLS)[UCOLS].values
        mats[(rg, model)] = (acc / NSEED).T          # (client, round)
        print(f"bonus loaded adult {rg} {model}")
vmax = np.percentile(np.stack(list(mats.values())), 99.5)  # shared scale
for (rg, model), M in mats.items():
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    im = ax.imshow(M, aspect="auto", cmap="viridis", vmin=0.0, vmax=vmax,
                   interpolation="nearest")
    for _, lo, hi in BLOCKS[:-1]:
        ax.axhline(hi - 0.5, color="white", lw=0.8)
    # stagger the three tiny groups' labels so they don't collide
    ax.set_yticks([(lo + hi - 1) / 2 for _, lo, hi in BLOCKS[:2]])
    ax.set_yticklabels([b[0] for b in BLOCKS[:2]], fontsize=8)
    for (label, lo, hi), xoff in zip(BLOCKS[2:], (-0.02, -0.10, -0.18)):
        ax.annotate(label, xy=(0, (lo + hi - 1) / 2),
                    xycoords=("axes fraction", "data"),
                    xytext=(xoff, (lo + hi - 1) / 2), textcoords=("axes fraction", "data"),
                    fontsize=7, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color="0.4"))
    ax.set_xlabel("round")
    ax.set_ylabel("client (grouped by race)", labelpad=28)
    cfg = ""
    if model in ("fedavot_cvar", "fedcvar"):
        a, g = CFG[("adult", rg, model)]
        cfg = f" ($\\alpha$={a:.1f}, $\\gamma$={g:.1f})"
    ax.set_title(f"adult / {rg} — {NAMES[model]}{cfg}\nper-client loss"
                 f" (5-seed mean)", fontsize=10)
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(f"loss (clipped at {vmax:.2f} = p99.5)")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}bonus_userheat_adult_{rg}_{model}.{ext}", dpi=150)
    plt.close(fig)
print("done ->", OUT)
