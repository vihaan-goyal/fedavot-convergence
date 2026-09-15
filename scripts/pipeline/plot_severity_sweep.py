# Figure + table for scripts/pipeline/severity_sweep.sh: tail loss vs infeasible importance mass,
# FedAVOT / uniform-over-K / full, measured (solid, 5 seeds, +-1 std band) against the exact
# loss floor each rule converges toward (dashed; closed-form LS on IMDb-Wiki, Newton logistic on
# Adult). Bias = floor gap; variance = measured minus floor.
# Usage: .venv/Scripts/python.exe scripts/pipeline/plot_severity_sweep.py
import os, sys, csv, glob, re, statistics as st
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_experiments as RE
from alignment_diagnostic import cell_marginals, cell_floors

ROOT = "results/2026-09-14_severity_sweep"
FIG = "figures/2026-09-14_severity_sweep"
COL = {"fedavot": "tab:blue", "fedavg": "tab:orange", "full": "tab:red"}
LBL = {"fedavot": "FedAVOT", "fedavg": "Uniform average over K", "full": "Full participation"}
DS_LABEL = {"imdbwiki": "IMDb-Wiki age regression (MSE)", "adult": "Adult income (cross-entropy)"}
TAG_LABEL = {"const": "constant learning rate", "decay1000": r"learning-rate decay $\eta_t=\eta/(1+t/1000)$"}

args = RE.parse_args([])
N, K = args.num_users, args.k
data = {}
rows = []
for cell in sorted(glob.glob(os.path.join(ROOT, "*_*"))):
    if not os.path.isdir(cell) or not os.path.exists(os.path.join(cell, "summary.csv")):
        continue
    name = os.path.basename(cell)
    m = re.match(r"(imdb|adult)_(beta([\d.]+)|feasible)_(const|decay\d+)", name)
    if not m:
        continue
    ds = "imdbwiki" if m.group(1) == "imdb" else "adult"
    regime = "feasible" if m.group(2) == "feasible" else "infeasible"
    beta = float(m.group(3)) if m.group(3) else None
    tag = m.group(4)
    if ds not in data:
        data[ds] = RE.load_imdbwiki(args) if ds == "imdbwiki" else RE.load_adult(args)
    tpath = os.path.join(cell, f"transport_{ds}_{regime}_K{K}.npz")
    p, pi, p_hat, p_til, inf_mass = cell_marginals(tpath, N, K)
    floors = cell_floors(data[ds], p, p_hat, p_til)
    srows = list(csv.DictReader(open(os.path.join(cell, "summary.csv"))))
    meas = {}
    for mdl in COL:
        v = [float(r["overall_tail"]) for r in srows if r["model"] == mdl]
        meas[mdl] = (st.mean(v), st.pstdev(v), len(v)) if v else (np.nan, np.nan, 0)
    rows.append(dict(dataset=ds, regime=regime, beta=beta, tag=tag, n_infeasible=int((p > pi).sum()),
                     infeasible_mass=inf_mass, l1_p_phat=float(np.abs(p - p_hat).sum()),
                     l1_p_ptilde=float(np.abs(p - p_til).sum()),
                     **{f"floor_{k}": v for k, v in floors.items()},
                     **{f"meas_{k}": meas[k][0] for k in COL}, **{f"std_{k}": meas[k][1] for k in COL},
                     n_seeds=meas["fedavot"][2]))

os.makedirs(FIG, exist_ok=True)
with open(os.path.join(FIG, "severity_sweep_table.csv"), "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)

print(f"{'cell':26s} {'#inf':>4} {'mass%':>6} | {'floor OT':>9} {'floor unif':>10} {'floor full':>10} | "
      f"{'meas OT':>9} {'meas unif':>9} {'meas full':>9} | {'unif-OT':>8} {'seeds':>5}")
for r in rows:
    print(f"{r['dataset']+'/'+(f'b{r[chr(98)+chr(101)+chr(116)+chr(97)]}' if r['beta'] is not None else 'feas')+'/'+r['tag']:26s} "
          f"{r['n_infeasible']:4d} {100*r['infeasible_mass']:6.1f} | {r['floor_fedavot']:9.4f} {r['floor_fedavg']:10.4f} "
          f"{r['floor_full']:10.4f} | {r['meas_fedavot']:9.4f} {r['meas_fedavg']:9.4f} {r['meas_full']:9.4f} | "
          f"{r['meas_fedavg']-r['meas_fedavot']:8.4f} {r['n_seeds']:5d}")

tags = sorted({r["tag"] for r in rows}, key=lambda t: (t != "const", t))
fig, axes = plt.subplots(2, len(tags), figsize=(5.2 * len(tags), 7.6), squeeze=False)
for i, ds in enumerate(["imdbwiki", "adult"]):
    for j, tag in enumerate(tags):
        ax = axes[i, j]
        sel = sorted([r for r in rows if r["dataset"] == ds and r["tag"] == tag and r["beta"] is not None],
                     key=lambda r: r["infeasible_mass"])
        if not sel:
            ax.set_visible(False); continue
        x = np.array([100 * r["infeasible_mass"] for r in sel])
        for mdl in ["full", "fedavg", "fedavot"]:
            y = np.array([r[f"meas_{mdl}"] for r in sel]); s = np.array([r[f"std_{mdl}"] for r in sel])
            fl = np.array([r[f"floor_{mdl}"] for r in sel])
            ax.plot(x, y, "o-", color=COL[mdl], lw=2, ms=6, label=f"{LBL[mdl]} (measured)")
            ax.fill_between(x, y - s, y + s, color=COL[mdl], alpha=0.15, lw=0)
            ax.plot(x, fl, "--", color=COL[mdl], lw=1.4, label=f"{LBL[mdl]} (exact floor)" if mdl != "full" else None)
        for r in sel:   # direct-label the betas
            ax.annotate(rf"$\beta$={r['beta']:g}", (100 * r["infeasible_mass"], r["meas_fedavg"]),
                        textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7, color="0.35")
        if ds == "imdbwiki":
            ax.set_yscale("log")
        ax.set_xlabel(r"importance mass that is infeasible, $\sum_{p_i>\pi_i} p_i$ (%)")
        ax.set_ylabel("tail-500 loss, p-weighted")
        ax.set_title(f"{DS_LABEL[ds]}\n{TAG_LABEL.get(tag, tag)}", fontsize=10)
        ax.grid(alpha=0.25)
        if i == 0 and j == 0:
            ax.legend(fontsize=7.5, loc="upper left")
fig.suptitle("Infeasibility severity sweep: measured tail loss vs the floor each aggregation rule converges to\n"
             "(solid = 5-seed mean ±1 std, dashed = exact optimum of the objective the rule actually minimises)",
             fontsize=10.5)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"severity_sweep_K{K}_{args.rounds}rounds.{ext}"), dpi=160)
print(f"\nsaved {FIG}/severity_sweep_K{K}_{args.rounds}rounds.png/.pdf and severity_sweep_table.csv")
