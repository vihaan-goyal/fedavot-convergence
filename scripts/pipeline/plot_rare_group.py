# Herlock's 2026-09-15 metric request: report the loss on the LEAST REPRESENTED critical group,
# not the overall objective. Rare group = Adult "Other" (the smallest race: one group of 30 out
# of 100; Amer-Indian-Eskimo also reported) and IMDb-Wiki tier 1 (the 20 highest-importance
# identities, which under r ~ i^beta with beta > 0 are the least observed ones).
# Reads only the per-run tail stats already in results/2026-09-14_severity_sweep/<cell>/summary.csv
# (no retraining) and the infeasible mass per cell from the severity sweep table.
# Usage: .venv/Scripts/python.exe scripts/pipeline/plot_rare_group.py
import os, csv, glob, re, statistics as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "results/2026-09-14_severity_sweep"
NU_TABLE = "figures/2026-09-14_severity_sweep/severity_sweep_table.csv"
OUT = "figures/2026-09-17_rare_group"
PAPER_FIGS = "paper/gavot_draft/figs"
RARE = {"adult": ["Other", "Amer-Indian-Eskimo"], "imdbwiki": ["tier1"]}
MODELS = ["fedavot", "fedavg", "fedavg_mk", "full"]
COL = {"fedavot": "tab:blue", "fedavg": "tab:orange", "fedavg_mk": "tab:green", "full": "tab:red"}
LBL = {"fedavot": "FedAVOT", "fedavg": "group-blind avg.", "fedavg_mk": r"fixed multiplier $m/K$", "full": "full"}
TAG_LBL = {"const": "constant stepsize", "decay1000": r"$\eta_t=\eta/(1+t/1000)$"}
YLBL = {"adult": "cross-entropy, race = Other", "imdbwiki": "MSE, top-importance identities"}

nu = {}
for r in csv.DictReader(open(NU_TABLE)):
    b = None if r["beta"] in ("", "None") else float(r["beta"])
    nu[(r["dataset"], r["regime"], b, r["tag"])] = float(r["infeasible_mass"])

rows = []
for cell in sorted(glob.glob(os.path.join(ROOT, "*_*"))):
    name = os.path.basename(cell)
    m = re.match(r"(imdb|adult)_(beta([\d.]+)|feasible)_(const|decay\d+)$", name)
    if not m or not os.path.exists(os.path.join(cell, "summary.csv")):
        continue
    ds = "imdbwiki" if m.group(1) == "imdb" else "adult"
    regime = "feasible" if m.group(2) == "feasible" else "infeasible"
    beta = float(m.group(3)) if m.group(3) else None
    tag = m.group(4)
    srows = list(csv.DictReader(open(os.path.join(cell, "summary.csv"))))
    for grp in RARE[ds]:
        for mdl in MODELS:
            v = [float(r[f"group_tail_{grp}"]) for r in srows if r["model"] == mdl]
            ov = [float(r["overall_tail"]) for r in srows if r["model"] == mdl]
            if not v:
                continue
            rows.append(dict(cell=name, dataset=ds, regime=regime, beta=beta, tag=tag,
                             nu=nu.get((ds, regime, beta, tag)), group=grp, model=mdl, n_seeds=len(v),
                             rare_mean=st.mean(v), rare_std=st.pstdev(v),
                             overall_mean=st.mean(ov), overall_std=st.pstdev(ov)))

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "rare_group_table.csv"), "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

def pick(ds, grp, tag, mdl):
    return sorted([r for r in rows if r["dataset"] == ds and r["group"] == grp and r["tag"] == tag
                   and r["model"] == mdl and r["regime"] == "infeasible"], key=lambda r: r["nu"])

for ds, grp, fname in [("imdbwiki", "tier1", "rare_group_imdb"), ("adult", "Other", "rare_group_adult")]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 1.9), sharey=True)
    for ax, tag in zip(axes, ["const", "decay1000"]):
        for mdl in ["fedavot", "fedavg", "full"]:
            pts = pick(ds, grp, tag, mdl)
            if ds == "adult":   # two Adult cells share nu = .60; sweep axis is beta (r ~ p^beta), aligned on the left
                pts = sorted(pts, key=lambda r: -r["beta"])
                x = [r["beta"] for r in pts]
            else:
                x = [100 * r["nu"] for r in pts]
            y = [r["rare_mean"] for r in pts]; s = [r["rare_std"] for r in pts]
            ax.errorbar(x, y, yerr=s, color=COL[mdl], marker="o", ms=3, lw=1.2, capsize=2, label=LBL[mdl])
        ax.set_title(TAG_LBL[tag], fontsize=8)
        if ds == "adult":
            ax.invert_xaxis()
            ax.set_xlabel(r"$\beta$ in $r\propto p^{\beta}$ (aligned $\to$ prevalence; $\nu$ = 0, 0, .40, .60, .60)", fontsize=7.5)
        else:
            ax.set_xlabel(r"infeasible mass $\nu$ (%)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(YLBL[ds], fontsize=7.5)
    axes[1].legend(fontsize=7, frameon=False)
    fig.tight_layout(pad=0.4)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{fname}.{ext}"), dpi=200, bbox_inches="tight")
    fig.savefig(os.path.join(PAPER_FIGS, f"{fname}.pdf"), bbox_inches="tight")
    plt.close(fig)

head = [("adult", "infeasible", 0.0, "Adult, prevalence"), ("adult", "infeasible", 1.0, "Adult, aligned"),
        ("imdbwiki", "infeasible", 0.0, "IMDb, skewed"), ("imdbwiki", "feasible", None, "IMDb, aligned")]
def fmt(ds, v, s, mdl):
    if v != v: return "--"
    if mdl == "fedavg_mk" and (v > 1e6): return "div."
    return f"{v:.4f} +- {s:.4f}" if ds == "adult" else f"{v:.2f} +- {s:.2f}"
lines = ["# Least-represented-group loss, decaying stepsize, tail-500 over 5 seeds (population std)",
         "", "Adult: race = Other (smallest category; 1 group of 30). IMDb-Wiki: tier 1 = 20 highest-importance identities (least observed when beta > 0).", ""]
for grp_ds, grps in RARE.items():
    for grp in grps:
        lines += [f"## {grp_ds}: group {grp}, headline cells", "", "| Instance | nu | FedAVOT | group-blind avg. | m/K | full |", "|---|---|---|---|---|---|"]
        for ds, regime, beta, label in head:
            if ds != grp_ds: continue
            cells = {}
            for mdl in MODELS:
                rr = [r for r in rows if r["dataset"] == ds and r["regime"] == regime and r["beta"] == beta
                      and r["tag"] == "decay1000" and r["group"] == grp and r["model"] == mdl]
                cells[mdl] = (rr[0]["rare_mean"], rr[0]["rare_std"]) if rr else (float("nan"), float("nan"))
            n = nu.get((ds, regime, beta, "decay1000"))
            lines.append(f"| {label} | {n:.2f} | " + " | ".join(fmt(ds, *cells[m], m) for m in MODELS) + " |")
        lines.append("")
for ds, grp in [("adult", "Other"), ("adult", "Amer-Indian-Eskimo"), ("imdbwiki", "tier1")]:
    lines += [f"## {ds} sweep, group {grp}", "", "| beta | nu | stepsize | FedAVOT | group-blind avg. | full | gain (avg - FedAVOT) |", "|---|---|---|---|---|---|---|"]
    for tag in ["const", "decay1000"]:
        for r in pick(ds, grp, tag, "fedavot"):
            u = [x for x in pick(ds, grp, tag, "fedavg") if x["beta"] == r["beta"]][0]
            fu = [x for x in pick(ds, grp, tag, "full") if x["beta"] == r["beta"]][0]
            d = 4 if ds == "adult" else 2
            lines.append(f"| {r['beta']} | {r['nu']:.2f} | {tag} | {r['rare_mean']:.{d}f} | {u['rare_mean']:.{d}f} | {fu['rare_mean']:.{d}f} | {u['rare_mean'] - r['rare_mean']:+.{d}f} |")
    lines.append("")
open(os.path.join(OUT, "rare_group_headline.md"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
