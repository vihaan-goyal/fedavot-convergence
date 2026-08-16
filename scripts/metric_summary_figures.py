# Discord-facing summary figures built from the curated sweep metric tables
# (sheets_export/*.csv) -- no retraining, no raw-sweep CSVs needed. Run from
# the repo root.
#
# Outputs (figures/2026-08-14_metric_summary/):
#   severity_inversion.{png,pdf} -- tail loss relative to full participation,
#       FedAVOT vs plain uniform-over-K averaging, across the four
#       dataset x regime settings ordered by infeasible p-mass. Uniform wins
#       only under SEVERE infeasibility (IMDb-Wiki mirrored, 88% starved
#       mass); FedAVOT wins under mild infeasibility (Adult, 60%) and in
#       both feasible regimes.
#   group_tail_bars.{png,pdf} -- standalone per-critical-group tail-loss
#       bars at the pinned (alpha, gamma) = (0.3, 0.3) config (same series
#       as the Google Sheet; a cleaner cut of the bar panel embedded in the
#       pipeline's *_groups figures).

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BEST_TABLE = "sheets_export/best_table.csv"
GROUP_TAILS = "sheets_export/group_tails.csv"
OUT_DIR = "figures/2026-08-14_metric_summary"
DPI = 200

# house palette: FedAVOT blue, FedAvg orange, full red, CVaR-combination
# green, CVaR-uniform purple
COL = {"fedavot": "tab:blue", "fedavot_cvar": "tab:green",
       "fedcvar": "tab:purple", "fedavg": "tab:orange", "full": "tab:red"}
# sheets_export method column -> model key
SHEET_COLS = {
    "FedAVOT": "fedavot",
    "FedAVOT + CVaR (a=0.3, g=0.3)": "fedavot_cvar",
    "FedCVaR uniform agg (a=0.3, g=0.3)": "fedcvar",
    "FedAvg (uniform over K)": "fedavg",
    "FedAvg (full)": "full",
}
DS_LABEL = {"imdbwiki": "IMDb-Wiki", "adult": "Adult"}

# ordered by severity: infeasible-user p-mass 87.7% / 60% / 0 / 0
SETTINGS = [
    ("imdbwiki", "infeasible", "IMDb-Wiki mirrored\ninfeasible, 88% starved p-mass"),
    ("adult", "infeasible", "Adult prevalence\ninfeasible, 60% starved p-mass"),
    ("imdbwiki", "feasible", "IMDb-Wiki aligned\nfeasible"),
    ("adult", "feasible", "Adult aligned\nfeasible"),
]


def save(fig, stem):
    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT_DIR, f"{stem}.{ext}"),
                    dpi=DPI if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {OUT_DIR}/{stem}.png/.pdf")


def fig_severity_inversion():
    bt = pd.read_csv(BEST_TABLE)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    xs = np.arange(len(SETTINGS))
    wd = 0.32
    for k, (model, label) in enumerate(
            [("fedavot", "FedAVOT"), ("fedavg", "FedAvg (uniform over K)")]):
        rel, err = [], []
        for ds, regime, _ in SETTINGS:
            sub = bt[(bt.dataset == ds) & (bt.regime == regime)]
            full = float(sub[sub.model == "full"].overall_tail_mean.iloc[0])
            row = sub[sub.model == model]
            rel.append(float(row.overall_tail_mean.iloc[0]) / full)
            err.append(float(row.overall_tail_std.iloc[0]) / full)
        bars = ax.bar(xs + (k - 0.5) * wd, rel, wd, color=COL[model],
                      label=label, yerr=err, capsize=3, error_kw={"lw": 0.8})
        for b, v in zip(bars, rel):
            ax.annotate(f"{v:.3f}x", (b.get_x() + b.get_width() / 2, v),
                        ha="center", va="bottom", fontsize=7.5)
    ax.axhline(1.0, color=COL["full"], ls="--", lw=1.2)
    ax.annotate("FedAvg (full) = 1", (xs[-1] + 2 * wd, 1.0), ha="right",
                va="bottom", fontsize=8, color=COL["full"])
    ax.set_xticks(xs)
    ax.set_xticklabels([lab for _, _, lab in SETTINGS], fontsize=8.5)
    ax.set_ylabel("tail-500 loss relative to full participation")
    ax.set_ylim(0, 1.55)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title("Uniform averaging wins only under severe infeasibility\n"
                 "(tail-500 mean over 5 seeds, each model at its best config)",
                 fontsize=11)
    fig.tight_layout()
    save(fig, "severity_inversion")


def fig_group_tail_bars():
    gt = pd.read_csv(GROUP_TAILS)
    panels = [("imdbwiki", "infeasible"), ("imdbwiki", "feasible"),
              ("adult", "infeasible"), ("adult", "feasible")]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))
    cols = list(SHEET_COLS)
    for ax, (ds, regime) in zip(axes.ravel(), panels):
        sub = gt[(gt.dataset == ds) & (gt.regime == regime)]
        groups = sub.critical_group.tolist()
        xs = np.arange(len(groups))
        wd = 0.8 / len(cols)
        bar_max = 0.0
        for k, c in enumerate(cols):
            vals = sub[c].astype(float).values
            bar_max = max(bar_max, vals.max())
            ax.bar(xs + (k - (len(cols) - 1) / 2) * wd, vals, wd,
                   color=COL[SHEET_COLS[c]], label=c)
        ax.set_ylim(0, 1.25 * bar_max)   # paper bar convention
        ax.set_xticks(xs)
        ax.set_xticklabels([g.replace("-", "-\n") for g in groups], fontsize=8)
        ax.set_title(f"{DS_LABEL[ds]}, {regime.upper()}", fontsize=11)
        ax.set_ylabel("tail-500 group loss", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(labelsize=8)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.suptitle("Loss per critical group, CVaR models at (alpha, gamma) = (0.3, 0.3)",
                 fontsize=12)
    fig.legend(handles, labels, loc="upper center", ncol=5, fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, 0.955))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "group_tail_bars")


if __name__ == "__main__":
    fig_severity_inversion()
    fig_group_tail_bars()
