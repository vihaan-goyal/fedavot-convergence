# Paper Fig. 2 (GAVOT draft): IMDb-Wiki overall loss vs infeasible mass, constant vs decaying
# stepsize, measured tail-500 (solid, +-1 std) against the exact floors Phi (dashed).
# Reads figures/2026-09-14_severity_sweep/severity_sweep_table.csv (no retraining) and writes
# paper/gavot_draft/figs/severity_imdb.{pdf,png}. Titling matches the rare-group figures.
# Usage: .venv/Scripts/python.exe scripts/pipeline/plot_severity_paper.py
import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

TABLE = "figures/2026-09-14_severity_sweep/severity_sweep_table.csv"
OUT = "paper/gavot_draft/figs"
COL = {"fedavot": "tab:blue", "fedavg": "tab:orange", "full": "tab:red"}
LBL = {"fedavot": "GAVOT", "fedavg": "group-blind avg.", "full": "full"}
MK = {"fedavot": "o", "fedavg": "s", "full": "^"}; LS = {"fedavot": "-", "fedavg": "--", "full": ":"}
plt.rcParams["pdf.fonttype"] = 42  # Type 1/TrueType, not Type 3 (ICASSP kit)
PANEL = {"const": "constant stepsize", "decay1000": "decaying stepsize"}

rows = [r for r in csv.DictReader(open(TABLE)) if r["dataset"] == "imdbwiki" and r["regime"] == "infeasible"]
fig, axes = plt.subplots(1, 2, figsize=(3.35, 1.65), sharey=True)
for ax, tag in zip(axes, ["const", "decay1000"]):
    pts = sorted([r for r in rows if r["tag"] == tag], key=lambda r: float(r["infeasible_mass"]))
    x = [100 * float(r["infeasible_mass"]) for r in pts]
    for m in ["fedavot", "fedavg", "full"]:
        y = [float(r[f"meas_{m}"]) for r in pts]; s = [float(r[f"std_{m}"]) for r in pts]
        ax.errorbar(x, y, yerr=s, color=COL[m], marker=MK[m], ls=LS[m], ms=3, lw=1.3, capsize=2, label=LBL[m] + ", measured")
        if m != "full":
            ax.plot(x, [float(r[f"floor_{m}"]) for r in pts], color=COL[m], ls="--", lw=1.0, label=LBL[m] + r", floor $\Phi$")
    for r, xi in zip(pts, x):
        ax.annotate(rf"$\beta$={float(r['beta']):g}", (xi, float(r["meas_fedavot"])), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=6, color="0.3")
    ax.set_title(PANEL[tag], fontsize=7)
    ax.set_xlabel(r"infeasible mass $\nu$ (%)", fontsize=7); ax.tick_params(labelsize=7)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
axes[0].set_ylabel(r"$F_p$ (MSE)", fontsize=7)

_h, _l = axes[0].get_legend_handles_labels(); _sel = [i for i, t in enumerate(_l) if "measured" in t]
axes[0].legend([_h[i] for i in _sel], [_l[i].replace(", measured", "") for i in _sel], fontsize=6.5, frameon=False, loc="lower right", handlelength=2.2)
fig.tight_layout(pad=0.4)
os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, "severity_imdb.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "severity_imdb.png"), dpi=200, bbox_inches="tight")
print("wrote", OUT + "/severity_imdb.{pdf,png}")
