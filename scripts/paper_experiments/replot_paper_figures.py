# Regenerate the three curve-based paper figures from the saved npz curves, with the
# de-federated vocabulary Herlock asked for on 2026-07-27 (the paper is framed as fair
# optimization, not federated learning, so "users/clients/rounds/FedAvg(K)" must not
# appear inside the figures either).  No retraining: the numbers quoted in the tex are
# the ones in these npz files.
#
#   users / clients      -> critical groups
#   round                -> iteration
#   FedAvg(K)            -> fixed multiplier m/K
#   FedAvg(full)         -> full coverage
#   FedAVOT              -> unchanged (kept as a proper name)
#
# The two synthetic figures (fedavot_phase_boundary, fedavot_mechanism) have no saved
# curves; their labels were edited in phase_boundary_experiment.py and
# feasibility_diagnostic.py and those scripts were re-run.
import numpy as np
import matplotlib.pyplot as plt

K = 3
COL = {"avot": "tab:blue", "faK": "tab:orange", "full": "tab:red"}
LBL = {"avot": f"FedAVOT (K={K})",
       "faK": f"Fixed multiplier $m/K$ (K={K})",
       "full": "Full coverage"}
DIVERGE_NOTE = ("Fixed multiplier diverges (off scale):\n"
                "$m/K$ scaling assumes a uniform observation rate")


def plot_curve(ax, L, label, color, band=True):
    mean, std = np.mean(L, axis=0), np.std(L, axis=0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=label, color=color)
    if band:
        ax.fill_between(x, np.maximum(mean-std, 1e-3), mean+std, color=color, alpha=0.15)


# ================================================================
# IMDb-Wiki, both availability regimes
# ================================================================
IMDB = [
    dict(tag="infeasible", rounds=4000,
         title=("IMDb-Wiki age regression, INFEASIBLE availability (mirrored cubic $r$), "
                "{rounds} iterations, {seeds} seeds\n"
                "88% of the importance mass is unreachable, so FedAVOT and the fixed "
                "multiplier both plateau above full coverage")),
    dict(tag="feasible", rounds=5000,
         title=("IMDb-Wiki age regression, FEASIBLE availability (aligned linear $r$), "
                "{rounds} iterations, {seeds} seeds\n"
                "$p_i \\leq \\pi_i$ holds for every group, so FedAVOT reaches full "
                "coverage on real data")),
]

for cfg in IMDB:
    d = np.load(f"data/imdbwiki_{cfg['tag']}_K{K}_{cfg['rounds']}rounds_curves.npz")
    fedot, faK, full = d["fedot"], d["faK"], d["full"]
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_curve(ax, fedot, LBL["avot"], COL["avot"])
    plot_curve(ax, faK, LBL["faK"], COL["faK"], band=False)
    plot_curve(ax, full, LBL["full"], COL["full"])
    ax.set_yscale("log")
    lo = 0.85 * min(np.mean(fedot, axis=0).min(), np.mean(full, axis=0).min())
    hi = 1.35 * max(np.mean(fedot, axis=0).max(), np.mean(full, axis=0).max())
    ax.set_ylim(lo, hi)
    if np.mean(faK, axis=0).max() > hi:
        ax.annotate(DIVERGE_NOTE, xy=(0.02, 0.97), xycoords="axes fraction", va="top",
                    fontsize=9, color=COL["faK"])
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Importance-weighted MSE $F_p(\\theta)$ (log)")
    ax.set_title(cfg["title"].format(rounds=cfg["rounds"], seeds=fedot.shape[0]))
    ax.legend(); ax.grid(alpha=0.3)
    stem = f"figures/2026-07-27_paper/imdbwiki_{cfg['tag']}_K{K}_{cfg['rounds']}rounds"
    fig.savefig(f"{stem}.png", dpi=140, bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"saved {stem}.png/.pdf")

# ================================================================
# Adult: two regimes x (trajectory, per-category bars)
# ================================================================
ROUNDS, TAIL = 2000, 500
d = np.load("data/adult_race_K3_2000rounds_curves.npz", allow_pickle=True)
GROUP_NAMES = [str(g) for g in d["group_names"]]
NG = len(GROUP_NAMES)
NUM_GROUPS = len(d["p"])
K_CAP = 1e12
TITLES = {"prevalence": "Prevalence availability (every group equally observable): INFEASIBLE",
          "aligned": "Importance-aligned availability: FEASIBLE"}

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
for col, regime in enumerate(("prevalence", "aligned")):
    F = {m: d[f"{regime}_{m}_F"] for m in ("avot", "faK", "full")}
    G = {m: d[f"{regime}_{m}_G"] for m in ("avot", "faK", "full")}
    k_diverged = bool(F["faK"].max() >= K_CAP)

    ax = axes[0, col]
    for m in ("avot", "faK", "full"):
        if m == "faK" and k_diverged:
            continue
        mean, std = F[m].mean(axis=0), F[m].std(axis=0)
        ax.plot(mean, color=COL[m], label=LBL[m], lw=1.3)
        if m != "faK":
            ax.fill_between(np.arange(len(mean)), mean-std, mean+std,
                            color=COL[m], alpha=0.15)
    ax.set_yscale("log"); ax.set_ylim(0.18, 3.0)
    if k_diverged:
        ax.annotate("Fixed multiplier diverges:\n$m/K$ scaling assumes\n"
                    "a uniform observation rate",
                    xy=(0.03, 0.35), xycoords="axes fraction", va="top",
                    fontsize=9, color=COL["faK"])
    ax.set_xlabel("Iteration")
    ax.set_ylabel(r"Objective $F(\theta)$ (category-uniform CE, log)")
    ax.set_title(TITLES[regime], fontsize=11)
    ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3, which="both")

    t0 = ROUNDS // 2
    axi = ax.inset_axes([0.42, 0.48, 0.55, 0.38])
    for m in ("avot", "full"):
        mean, std = F[m].mean(axis=0)[t0:], F[m].std(axis=0)[t0:]
        xz = np.arange(t0, ROUNDS)
        axi.plot(xz, mean, color=COL[m], lw=1.2)
        axi.fill_between(xz, mean-std, mean+std, color=COL[m], alpha=0.15)
    # keep this short: a longer inset title runs under the panel legend
    axi.set_title(f"zoom: iterations {t0}-{ROUNDS} (linear)", fontsize=8)
    axi.tick_params(labelsize=7); axi.grid(alpha=0.3)

    ax = axes[1, col]
    xs = np.arange(NG); wd = 0.26
    methods = ("avot", "full") if k_diverged else ("avot", "faK", "full")
    offs = {2: (-0.5, 0.5), 3: (-1, 0, 1)}[len(methods)]
    for k, m in enumerate(methods):
        gtail = G[m][:, -TAIL:, :].mean(axis=(0, 1))
        ax.bar(xs + offs[k]*wd, gtail, wd, color=COL[m], label=LBL[m])
    if k_diverged:
        ax.annotate("fixed multiplier diverged (omitted)", xy=(0.03, 0.96),
                    xycoords="axes fraction", va="top", fontsize=9, color=COL["faK"])
    ax.set_ylim(0, 1.25 * max(G[m][:, -TAIL:, :].mean(axis=(0, 1)).max()
                              for m in methods))
    ax.set_xticks(xs)
    ax.set_xticklabels([g.replace("-", "-\n") for g in GROUP_NAMES], fontsize=8)
    ax.set_ylabel(f"Final per-category CE (tail-{TAIL})")
    ax.set_title(f"Per-race CE, {regime} regime", fontsize=11)
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)

fig.suptitle("Adult income classification, uniform importance target over race "
             f"($m={NUM_GROUPS}$ critical groups, $K={K}$, {ROUNDS} iterations, "
             f"{d['prevalence_avot_F'].shape[0]} seeds)", fontsize=12)
fig.tight_layout()
fig.savefig(f"figures/2026-07-27_paper/adult_race_K{K}_{ROUNDS}rounds.png", dpi=140, bbox_inches="tight")
fig.savefig(f"figures/2026-07-27_paper/adult_race_K{K}_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/2026-07-27_paper/adult_race_K{K}_{ROUNDS}rounds.png/.pdf")
