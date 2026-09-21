"""Schedule comparison for the four headline cells (2026-09-20 sweep).

Reads summary.csv from results/2026-09-14_severity_sweep/<cell>_{const,decay1000} and
results/2026-09-20_lr_schedules/<cell>_<sched>, plus the exact floors from
figures/2026-09-14_severity_sweep/severity_sweep_table.csv, and prints one table per cell:
schedule, measured GAVOT / group-blind / full, residual above the exact floor for each,
gain (group-blind - GAVOT), Welch t (population std, 5 seeds). Writes the markdown to
paper/gavot_draft/review/LR_SCHEDULES_2026-09-20.md.
"""
import numpy as np, pandas as pd, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
SEV = ROOT / "results/2026-09-14_severity_sweep"
LRS = ROOT / "results/2026-09-20_lr_schedules"
FLOORS = pd.read_csv(ROOT / "figures/2026-09-14_severity_sweep/severity_sweep_table.csv")
CELLS = {  # cell prefix -> (dataset, regime, beta) in the floor table
    "adult_beta0.00": ("adult", "infeasible", 0.0),
    "adult_beta1.00": ("adult", "infeasible", 1.0),
    "imdb_beta0.00": ("imdbwiki", "infeasible", 0.0),
    "imdb_feasible": ("imdbwiki", "feasible", None),
}
TITLES = {"adult_beta0.00": "Adult infeasible (nu=.60)", "adult_beta1.00": "Adult feasible (nu=0)",
          "imdb_beta0.00": "IMDb infeasible (nu=.31)", "imdb_feasible": "IMDb feasible (nu=0)"}
SCHEDS = [("const", SEV, "const"), ("hyper250", LRS, "hyper250"), ("hyper1000", SEV, "decay1000"),
          ("hyper4000", LRS, "hyper4000"), ("hyper16000", LRS, "hyper16000"),
          ("sqrt250", LRS, "sqrt250"), ("sqrt1000", LRS, "sqrt1000"),
          ("step1000", LRS, "step1000"), ("cosine", LRS, "cosine")]
FORM = {"const": "eta", "hyper250": "eta/(1+t/250)", "hyper1000": "eta/(1+t/1000)",
        "hyper4000": "eta/(1+t/4000)", "hyper16000": "eta/(1+t/16000)",
        "sqrt250": "eta/sqrt(1+t/250)", "sqrt1000": "eta/sqrt(1+t/1000)",
        "step1000": "eta*0.5^floor(t/1000)", "cosine": "eta*(1+cos(pi t/R))/2"}

def welch(a, b):
    a, b = np.asarray(a), np.asarray(b); n = len(a)
    return (b.mean() - a.mean()) / np.sqrt(a.std() ** 2 / n + b.std() ** 2 / n)

out = []
for cell, (ds, reg, beta) in CELLS.items():
    f = FLOORS[(FLOORS.dataset == ds) & (FLOORS.regime == reg)]
    f = f[f.beta.isna()] if beta is None else f[f.beta == beta]
    f = f.iloc[0]
    fl = {"fedavot": f.floor_fedavot, "fedavg": f.floor_fedavg, "full": f.floor_full}
    dec = 4 if ds == "adult" else 2
    rows = []
    for name, base, suffix in SCHEDS:
        p = base / f"{cell}_{suffix}" / "summary.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p)
        g = {m: d[d.model == m].overall_tail.values for m in ("fedavot", "fedavg", "full")}
        mu = {m: v.mean() for m, v in g.items()}
        rows.append(dict(sched=name, form=FORM[name], gavot=mu["fedavot"], grp=mu["fedavg"], full=mu["full"],
                         r_full=mu["full"] - fl["full"], r_gavot=mu["fedavot"] - fl["fedavot"],
                         r_grp=mu["fedavg"] - fl["fedavg"], gain=mu["fedavg"] - mu["fedavot"],
                         t=welch(g["fedavot"], g["fedavg"]), sd=g["fedavot"].std()))
    rows.sort(key=lambda r: r["r_full"])
    best = rows[0]["sched"]
    out.append(f"\n### {TITLES[cell]}  (floors: GAVOT {fl['fedavot']:.{dec}f}, group-blind {fl['fedavg']:.{dec}f}, full {fl['full']:.{dec}f}; sorted by full-coverage residual)\n")
    out.append("| schedule | lr_t | GAVOT | group-blind | full | resid full | resid GAVOT | resid grp | gain | t | winner |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        w = "GAVOT" if r["gain"] > 0 else "group-blind"
        sig = "" if abs(r["t"]) >= 2.8 else " (n.s.)"
        out.append(f"| {r['sched']}{' **<- pick**' if r['sched']==best else ''} | {r['form']} | {r['gavot']:.{dec}f} | {r['grp']:.{dec}f} | {r['full']:.{dec}f} | {r['r_full']:.{dec}f} | {r['r_gavot']:.{dec}f} | {r['r_grp']:.{dec}f} | {r['gain']:+.{dec}f} | {r['t']:.1f} | {w}{sig} |")
md = "\n".join(out)
print(md)
(ROOT / "paper/gavot_draft/review/LR_SCHEDULES_2026-09-20.md").write_text(
    "# Stepsize schedule sweep, 2026-09-20\n\nRuns: `results/2026-09-20_lr_schedules/<cell>_<sched>/` (7 new schedules) plus const and hyper1000 "
    "from `results/2026-09-14_severity_sweep/`. 4000 steps, 5 seeds, tail-500, same eta and flags as the paper cells; "
    "every rule in a cell shares the schedule (method-neutral). Selection rule: the schedule with the smallest "
    "full-coverage residual (measured full minus exact floor), i.e. the one that optimizes the reference best, "
    "chosen without looking at GAVOT or group-blind. t = Welch t (population std, 5 seeds) for gain = group-blind - GAVOT; |t| < 2.8 marked n.s.\n"
    + md + "\n", encoding="utf-8")
