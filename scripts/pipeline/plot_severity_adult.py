# Adult companion to paper Fig. 2 (Herlock, 2026-09-22): overall loss vs availability skew, constant vs
# decaying stepsize, measured tail-500 (solid, +-1 std) against the exact floors Phi (dashed).
# x-axis is beta (sampling weights ~ p^beta), aligned (beta=1) on the left, because two Adult skews
# share nu = 0.60 and two share nu = 0. Reads the same severity_sweep_table.csv (no retraining) and
# writes paper/gavot_draft/figs/severity_adult.{pdf,png}. Style matches plot_severity_paper.py.
# Usage: .venv/Scripts/python.exe scripts/pipeline/plot_severity_adult.py
import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["pdf.fonttype"] = 42  # embed TrueType, not Type 3 (ICASSP kit)
MK = {"fedavot": "o", "fedavg": "s", "full": "^"}

TABLE = "figures/2026-09-14_severity_sweep/severity_sweep_table.csv"
OUT = "paper/gavot_draft/figs"
COL = {"fedavot": "tab:blue", "fedavg": "tab:orange", "full": "tab:red"}
LBL = {"fedavot": "GAVOT", "fedavg": "group-blind avg.", "full": "full"}
PANEL = {"const": r"constant stepsize $\eta$", "decay1000": r"decaying stepsize $\eta_t=\eta/(1+t/1000)$"}

rows = [r for r in csv.DictReader(open(TABLE)) if r["dataset"] == "adult" and r["regime"] == "infeasible"]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 1.8), sharey=True)
for ax, tag in zip(axes, ["const", "decay1000"]):
    pts = sorted([r for r in rows if r["tag"] == tag], key=lambda r: -float(r["beta"]))
    x = [float(r["beta"]) for r in pts]
    for m in ["fedavot", "fedavg", "full"]:
        y = [float(r[f"meas_{m}"]) for r in pts]; s = [float(r[f"std_{m}"]) for r in pts]
        ax.errorbar(x, y, yerr=s, color=COL[m], marker=MK[m], ms=3, lw=1.3, capsize=2, label=LBL[m])
        if m != "full":
            ax.plot(x, [float(r[f"floor_{m}"]) for r in pts], color=COL[m], ls="--", lw=1.0)
    ax.invert_xaxis()
    ax.set_xticks(x)
    ax.set_xticklabels([f"$\\beta$={float(r['beta']):g}\n$\\nu$={float(r['infeasible_mass']):.2f}" for r in pts], fontsize=9.3)
    ax.set_title(PANEL[tag], fontsize=9.3, pad=6)
    ax.set_xlabel(r"sampling weights $\propto p^{\beta}$", fontsize=9.3)
    ax.tick_params(labelsize=9.3)
    ax.grid(alpha=0.3)
axes[0].set_ylabel(r"overall loss $F_p$ (CE)", fontsize=9.3)
axes[1].legend(fontsize=9.3, frameon=False, loc="upper left", handlelength=2.2)
fig.tight_layout(pad=0.4)
os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, "severity_adult.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "severity_adult.png"), dpi=200, bbox_inches="tight")
print("wrote", OUT + "/severity_adult.{pdf,png}")
