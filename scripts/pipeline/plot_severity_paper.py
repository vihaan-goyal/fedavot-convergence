# Paper Fig. 2 (GAVOT draft): IMDb-Wiki overall loss vs infeasible mass, constant vs decaying
# stepsize, measured tail-500 (solid, +-1 std) against the exact floors Phi (dashed).
# Reads figures/2026-09-14_severity_sweep/severity_sweep_table.csv (no retraining) and writes
# paper/gavot_draft/figs/severity_imdb.{pdf,png}. Titling matches the rare-group figures.
# Usage: .venv/Scripts/python.exe scripts/pipeline/plot_severity_paper.py
import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["pdf.fonttype"] = 42  # embed TrueType, not Type 3 (ICASSP kit)
MK = {"fedavot": "o", "fedavg": "s", "fedavg_mk": "x", "full": "^"}

TABLE = "figures/2026-09-14_severity_sweep/severity_sweep_table.csv"
OUT = "paper/gavot_draft/figs"
COL = {"fedavot": "tab:blue", "fedavg": "tab:orange", "full": "tab:red"}
LBL = {"fedavot": "GAVOT", "fedavg": "group-blind avg.", "full": "full"}
PANEL = {"const": r"constant stepsize $\eta$", "decay1000": r"decaying stepsize $\eta_t=\eta/(1+t/1000)$"}

rows = [r for r in csv.DictReader(open(TABLE)) if r["dataset"] == "imdbwiki" and r["regime"] == "infeasible"]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 1.8), sharey=True)
for ax, tag in zip(axes, ["const", "decay1000"]):
    pts = sorted([r for r in rows if r["tag"] == tag], key=lambda r: float(r["infeasible_mass"]))
    x = [100 * float(r["infeasible_mass"]) for r in pts]
    for m in ["fedavot", "fedavg", "full"]:
        y = [float(r[f"meas_{m}"]) for r in pts]; s = [float(r[f"std_{m}"]) for r in pts]
        ax.errorbar(x, y, yerr=s, color=COL[m], marker=MK[m], ms=3, lw=1.3, capsize=2, label=LBL[m] + ", measured")
        if m != "full":
            ax.plot(x, [float(r[f"floor_{m}"]) for r in pts], color=COL[m], ls="--", lw=1.0, label=LBL[m] + r", floor $\Phi$")
    for r, xi in zip(pts, x):
        ax.annotate(rf"$\beta$={float(r['beta']):g}", (xi, float(r["meas_fedavot"])), textcoords="offset points",
                    xytext=((0, -11) if float(r["beta"]) == 2 else (0, 5)), ha=("right" if float(r["beta"]) == 3 else "center"), fontsize=8, color="0.3")
    ax.set_title(PANEL[tag], fontsize=9, pad=6); ax.tick_params(labelsize=8)
    ax.set_xlabel(r"infeasible mass $\nu$ (%)", fontsize=8.5)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
axes[0].set_ylabel(r"overall loss $F_p$ (MSE)", fontsize=9)

_h, _l = axes[1].get_legend_handles_labels(); _sel = [i for i, t in enumerate(_l) if "measured" in t]
axes[1].legend([_h[i] for i in _sel], [_l[i].replace(", measured", "") for i in _sel], fontsize=8, frameon=False, loc="upper left", handlelength=2.2)
fig.tight_layout(pad=0.4)
os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, "severity_imdb.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "severity_imdb.png"), dpi=200, bbox_inches="tight")
print("wrote", OUT + "/severity_imdb.{pdf,png}")
