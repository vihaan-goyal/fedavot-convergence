# Regenerate the three curve-based paper figures (IMDb-Wiki infeasible / feasible, Adult) in the
# SAME style as replot_paper_figures.py, but from the 2026-09-14 severity-sweep runs that use
# learning-rate decay (eta_t = eta / (1 + t/1000)) and, for the infeasible IMDb-Wiki panel, the
# uniform-availability regime (9/100 groups infeasible, 31% of the importance mass) instead of the
# mirrored-cubic support-collapse limit. Reads the pipeline CSVs (no retraining). Vocabulary is the
# de-federated one (critical groups / iterations / fixed multiplier m/K / full coverage).
#
#   .venv/Scripts/python.exe scripts/paper_experiments/replot_paper_figures_decay.py
import os, glob, gzip, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "results/2026-09-14_severity_sweep"
OUT = "figures/2026-09-14_paper"
K, TAIL = 3, 500
MODELS = ("fedavot", "fedavg", "fedavg_mk", "full")
COL = {"fedavot": "tab:blue", "fedavg": "tab:gray", "fedavg_mk": "tab:orange", "full": "tab:red"}
LBL = {"fedavot": f"FedAVOT (K={K})", "fedavg": f"Uniform average (K={K})",
       "fedavg_mk": f"Fixed multiplier $m/K$ (K={K})", "full": "Full coverage"}
BAND = {"fedavot", "fedavg", "full"}
CAP = 1e12
os.makedirs(OUT, exist_ok=True)


def load_cell(folder, dataset, regime):
    """{model: dict(F=(seeds, R), G=(seeds, R, NG))}, group names; models missing on disk are skipped."""
    out, gnames = {}, None
    for m in MODELS:
        files = sorted(glob.glob(os.path.join(folder, f"{dataset}_{regime}_{m}_seed*.csv.gz")))
        if not files:
            continue
        F, G = [], []
        for f in files:
            with gzip.open(f, "rt") as fh:
                rd = csv.reader(fh)
                head = next(rd)
                gi = [i for i, h in enumerate(head) if h.startswith("group_")]
                gnames = gnames or [head[i][6:] for i in gi]
                rows = np.array([[float(x) for x in r[:2 + len(gi)]] for r in rd])
            F.append(rows[:, 1])
            G.append(rows[:, 2:2 + len(gi)])
        out[m] = dict(F=np.stack(F), G=np.stack(G))
    return out, gnames


def plot_curve(ax, L, m, lw=1.3):
    mean, std = L.mean(0), L.std(0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=LBL[m], color=COL[m], lw=lw)
    if m in BAND:
        ax.fill_between(x, np.maximum(mean - std, 1e-3), mean + std, color=COL[m], alpha=0.15)


def tail(L):
    return L[:, -TAIL:].mean()


# ================================================================
# IMDb-Wiki, both availability regimes
# ================================================================
IMDB = [
    dict(folder="imdb_beta0.00_decay1000", regime="infeasible", tag="infeasible",
         title=("IMDb-Wiki age regression, INFEASIBLE availability (uniform $r$, skewed importance), "
                "{rounds} iterations, {seeds} seeds\n"
                "9/100 groups have $p_i > \\pi_i$ (31% of the importance mass): FedAVOT {ot:.1f} vs "
                "uniform average {un:.1f} vs full coverage {fu:.1f} (tail-{tail})")),
    dict(folder="imdb_feasible_decay1000", regime="feasible", tag="feasible",
         title=("IMDb-Wiki age regression, FEASIBLE availability (aligned linear $r$), "
                "{rounds} iterations, {seeds} seeds\n"
                "$p_i \\leq \\pi_i$ holds for every group: FedAVOT {ot:.1f} vs uniform average {un:.1f} "
                "vs full coverage {fu:.1f} (tail-{tail})")),
]
for cfg in IMDB:
    folder = os.path.join(ROOT, cfg["folder"])
    if not os.path.exists(os.path.join(folder, "summary.csv")):
        print(f"skip {cfg['folder']} (not finished)")
        continue
    D, _ = load_cell(folder, "imdbwiki", cfg["regime"])
    S, R = D["fedavot"]["F"].shape
    fig, ax = plt.subplots(figsize=(10, 6))
    ref = [D[m]["F"].mean(0) for m in ("fedavot", "fedavg", "full") if m in D]
    lo, hi = 0.85 * min(r.min() for r in ref), 1.35 * max(r.max() for r in ref)
    mk_off = "fedavg_mk" in D and D["fedavg_mk"]["F"].mean(0)[-TAIL:].max() > hi
    for m in MODELS:
        if m in D and not (m == "fedavg_mk" and mk_off):
            plot_curve(ax, D[m]["F"], m)
    ax.set_yscale("log")
    ax.set_ylim(lo, hi)
    if mk_off:
        mk_tail = tail(D["fedavg_mk"]["F"])
        what = "diverges" if mk_tail >= CAP else f"tail-{TAIL} = {mk_tail:.0f}, off scale (omitted)"
        ax.annotate(f"Fixed multiplier $m/K$ (K={K}): {what}\n$m/K$ scaling assumes a uniform observation rate",
                    xy=(0.02, 0.97), xycoords="axes fraction", va="top", fontsize=9, color=COL["fedavg_mk"])
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Importance-weighted MSE $F_p(\\theta)$ (log)")
    ax.set_title(cfg["title"].format(rounds=R, seeds=S, tail=TAIL, ot=tail(D["fedavot"]["F"]),
                                     un=tail(D["fedavg"]["F"]), fu=tail(D["full"]["F"])), fontsize=11)
    ax.legend()
    ax.grid(alpha=0.3)
    stem = f"{OUT}/imdbwiki_{cfg['tag']}_K{K}_{R}rounds_decay"
    fig.savefig(f"{stem}.png", dpi=140, bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"saved {stem}.png/.pdf")

# ================================================================
# Adult: two regimes x (trajectory, per-category bars)
# ================================================================
ADULT = {"prevalence": ("adult_beta0.00_decay1000",
                        "Prevalence availability (every group equally observable): INFEASIBLE"),
         "aligned": ("adult_beta1.00_decay1000", "Importance-aligned availability: FEASIBLE")}
cells = {k: load_cell(os.path.join(ROOT, f), "adult", "infeasible") for k, (f, _) in ADULT.items()
         if os.path.exists(os.path.join(ROOT, f, "summary.csv"))}
if len(cells) == 2:
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for col, regime in enumerate(("prevalence", "aligned")):
        D, gnames = cells[regime]
        R = D["fedavot"]["F"].shape[1]
        k_div = "fedavg_mk" in D and D["fedavg_mk"]["F"].max() >= CAP
        ax = axes[0, col]
        for m in MODELS:
            if m in D and not (m == "fedavg_mk" and k_div):
                plot_curve(ax, D[m]["F"], m)
        ax.set_yscale("log")
        ax.set_ylim(0.18, 3.0)
        if k_div:
            ax.annotate("Fixed multiplier diverges:\n$m/K$ scaling assumes\na uniform observation rate",
                        xy=(0.03, 0.35), xycoords="axes fraction", va="top", fontsize=9,
                        color=COL["fedavg_mk"])
        ax.set_xlabel("Iteration")
        ax.set_ylabel(r"Objective $F(\theta)$ (category-uniform CE, log)")
        ax.set_title(ADULT[regime][1], fontsize=11)
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(alpha=0.3, which="both")
        t0 = R // 2
        axi = ax.inset_axes([0.42, 0.48, 0.55, 0.38])
        for m in ("fedavot", "fedavg", "full"):
            if m not in D:
                continue
            mean, std = D[m]["F"].mean(0)[t0:], D[m]["F"].std(0)[t0:]
            xz = np.arange(t0, R)
            axi.plot(xz, mean, color=COL[m], lw=1.2)
            axi.fill_between(xz, mean - std, mean + std, color=COL[m], alpha=0.15)
        axi.set_title(f"zoom: iterations {t0}-{R} (linear)", fontsize=8)
        axi.tick_params(labelsize=7)
        axi.grid(alpha=0.3)

        ax = axes[1, col]
        methods = [m for m in MODELS if m in D and not (m == "fedavg_mk" and k_div)]
        xs = np.arange(len(gnames))
        wd = 0.8 / len(methods)
        for k, m in enumerate(methods):
            gt = D[m]["G"][:, -TAIL:, :].mean(axis=(0, 1))
            ax.bar(xs + (k - (len(methods) - 1) / 2) * wd, gt, wd, color=COL[m], label=LBL[m])
        if k_div:
            ax.annotate("fixed multiplier diverged (omitted)", xy=(0.03, 0.96), xycoords="axes fraction",
                        va="top", fontsize=9, color=COL["fedavg_mk"])
        ax.set_ylim(0, 1.25 * max(D[m]["G"][:, -TAIL:, :].mean(axis=(0, 1)).max() for m in methods))
        ax.set_xticks(xs)
        ax.set_xticklabels([g.replace("-", "-\n") for g in gnames], fontsize=8)
        ax.set_ylabel(f"Final per-category CE (tail-{TAIL})")
        ax.set_title(f"Per-race CE, {regime} regime", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    S = cells["prevalence"][0]["fedavot"]["F"].shape[0]
    fig.suptitle("Adult income classification, uniform importance target over race "
                 f"($m=100$ critical groups, $K={K}$, {R} iterations, {S} seeds, learning-rate decay)",
                 fontsize=12)
    fig.tight_layout()
    stem = f"{OUT}/adult_race_K{K}_{R}rounds_decay"
    fig.savefig(f"{stem}.png", dpi=140, bbox_inches="tight")
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    print(f"saved {stem}.png/.pdf")
else:
    print("skip adult (a regime is not finished)")
