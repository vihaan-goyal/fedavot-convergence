# Figure stage for the unified experiment runner (companion to run_experiments.py).
# Reads ONLY results/*.csv[.gz] + results/summary.csv -- no training code, no npz.
#
# Figures (all in the house style: log y, mean +- std seed band, png dpi140 + pdf):
#   overview   : overall loss, 5 curves per (dataset, regime) -- fedavot, fedavg, full
#                + the two CVaR models at their best (alpha, gamma) from the summary
#                (pin a specific config with --alpha/--gamma)
#   groups     : per-critical-group loss curves, 2x3 panels (5 groups + tail bars)
#   users      : per-user loss heat-strips (users sorted by importance rank), the
#                readable form of "loss per user for each round"
#   heatmaps   : (alpha, gamma) grid of tail overall / tail worst-group per CVaR model;
#                the gamma=1.00 row must match the grid-free fedavot/fedavg values
#                (built-in identity check); diverged cells are masked "DIV"
#   best-table : best (alpha, gamma) per model -> stdout + <fig-dir>/<prefix>best_table.csv
#
# summary.csv is preferred for tail stats / best-config selection; if it is missing,
# run `run_experiments.py --rebuild-summary` first (fallback here recomputes tails from
# the curve CSVs, which is slow for full grids).
import argparse
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FNAME_RE = re.compile(
    r"^(?P<dataset>adult|imdbwiki)_(?P<regime>feasible|infeasible)"
    r"_(?P<model>fedavot_cvar|fedcvar|fedavot|fedavg|full)"
    r"(?:_a(?P<alpha>\d+\.\d{2})_g(?P<gamma>\d+\.\d{2}))?"
    r"_seed(?P<seed>\d+)\.csv(?:\.gz)?$")

MODELS_ORDER = ("fedavot", "fedavot_cvar", "fedcvar", "fedavg", "full")
GRID_MODELS = ("fedavot_cvar", "fedcvar")
COL = {"fedavot": "tab:blue", "fedavot_cvar": "tab:green", "fedcvar": "tab:purple",
       "fedavg": "tab:orange", "full": "tab:red"}
LBL_FL = {"fedavot": "FedAVOT", "fedavot_cvar": "FedAVOT + CVaR",
          "fedcvar": "FedCVaR (uniform agg)", "fedavg": "FedAvg (uniform over K)",
          "full": "FedAvg (full)"}
LBL_DEFED = {"fedavot": "FedAVOT", "fedavot_cvar": "FedAVOT + CVaR",
             "fedcvar": "CVaR, uniform average", "fedavg": "Uniform average over K",
             "full": "Full coverage"}
SHORT = {"fedavot": "FedAVOT", "fedavot_cvar": "+CVaR", "fedcvar": "FedCVaR",
         "fedavg": "FedAvg(unif)", "full": "full"}
DS_LABEL = {"imdbwiki": "IMDb-Wiki age regression", "adult": "Adult income classification"}
YLABEL_FL = {"imdbwiki": "Global p-weighted MSE (log)",
             "adult": r"Objective $F(\theta)$ (group-uniform CE, log)"}
YLABEL_DEFED = {"imdbwiki": r"Importance-weighted MSE $F_p(\theta)$ (log)",
                "adult": r"Objective $F(\theta)$ (category-uniform CE, log)"}


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Build figures from run_experiments.py CSVs.")
    ap.add_argument("--results-dir", default="results", help="where the CSVs live")
    ap.add_argument("--fig-dir", default="figures", help="output directory")
    ap.add_argument("--figures", nargs="+", default=["overview", "groups", "users",
                                                     "heatmaps", "best-table"],
                    choices=["overview", "groups", "users", "heatmaps", "best-table"])
    ap.add_argument("--datasets", nargs="+", default=None, help="subset filter")
    ap.add_argument("--regimes", nargs="+", default=None, help="subset filter")
    ap.add_argument("--models", nargs="+", default=None, help="subset filter")
    ap.add_argument("--alpha", type=float, default=None,
                    help="pin the CVaR alpha shown in overview/groups/users "
                         "(default: best by tail overall from summary)")
    ap.add_argument("--gamma", type=float, default=None, help="pin the CVaR gamma")
    ap.add_argument("--tail", type=int, default=500,
                    help="tail window when recomputing without a summary")
    ap.add_argument("--vocab", default="fl", choices=["fl", "defed"],
                    help="label vocabulary (defed: Round->Iteration, critical groups)")
    ap.add_argument("--formats", nargs="+", default=["png", "pdf"], choices=["png", "pdf"])
    ap.add_argument("--dpi", type=int, default=140)
    ap.add_argument("--user-round-stride", type=int, default=0,
                    help="round stride for the users heat-strip (0 = auto ~R/1000)")
    ap.add_argument("--no-annot", action="store_true", help="suppress heatmap annotations")
    ap.add_argument("--prefix", default="exp_", help="figure filename prefix")
    ap.add_argument("--cap", type=float, default=1e12, help="divergence sentinel in the CSVs")
    return ap.parse_args(argv)


# ================================================================
# Data access
# ================================================================
def index_files(results_dir):
    rows = []
    for fname in os.listdir(results_dir):
        m = FNAME_RE.match(fname)
        if m:
            d = m.groupdict()
            rows.append(dict(dataset=d["dataset"], regime=d["regime"], model=d["model"],
                             alpha=d["alpha"] or "", gamma=d["gamma"] or "",
                             seed=int(d["seed"]), file=os.path.join(results_dir, fname)))
    if not rows:
        raise SystemExit(f"no experiment CSVs found in {results_dir}")
    return pd.DataFrame(rows)


def load_summary(results_dir):
    spath = os.path.join(results_dir, "summary.csv")
    if not os.path.exists(spath):
        return None
    s = pd.read_csv(spath, dtype=str, keep_default_na=False)
    for c in ("seed", "rounds", "diverged"):
        s[c] = s[c].astype(int)
    for c in [c for c in s.columns if c.endswith("_tail") or c.startswith("group_tail_")]:
        s[c] = pd.to_numeric(s[c].replace("", np.nan))
    return s


def read_cols(path, cols):
    return pd.read_csv(path, usecols=cols)


def stack_seed_curves(files, col):
    curves = [pd.read_csv(f, usecols=[col])[col].values for f in files]
    n = min(len(c) for c in curves)
    if len(set(len(c) for c in curves)) > 1:
        print(f"  warning: seed curves differ in length, truncating to {n}")
    return np.stack([c[:n] for c in curves])


def config_files(index, ds, regime, model, alpha="", gamma=""):
    sub = index[(index.dataset == ds) & (index.regime == regime) & (index.model == model)
                & (index.alpha == alpha) & (index.gamma == gamma)]
    return list(sub.sort_values("seed")["file"].values), list(sub.sort_values("seed")["seed"].values)


def tail_from_files(files, tail):
    vals = []
    for f in files:
        v = pd.read_csv(f, usecols=["overall"])["overall"].values
        vals.append(v[-tail:].mean())
    return np.array(vals)


def best_config(summary, index, ds, regime, model, args):
    # returns (alpha_str, gamma_str, mean_tail, std_tail) for a grid model
    if args.alpha is not None and args.gamma is not None:
        a, g = f"{args.alpha:.2f}", f"{args.gamma:.2f}"
        if summary is not None:
            sub = summary[(summary.dataset == ds) & (summary.regime == regime)
                          & (summary.model == model) & (summary.alpha == a)
                          & (summary.gamma == g)]
            return a, g, sub.overall_tail.mean(), sub.overall_tail.std(ddof=0)
        files, _ = config_files(index, ds, regime, model, a, g)
        t = tail_from_files(files, args.tail)
        return a, g, t.mean(), t.std(ddof=0)
    if summary is not None:
        sub = summary[(summary.dataset == ds) & (summary.regime == regime)
                      & (summary.model == model) & (summary.alpha != "")]
        if len(sub) == 0:
            return None
        grp = sub.groupby(["alpha", "gamma"])["overall_tail"].agg(["mean", lambda v: v.std(ddof=0)])
        grp.columns = ["mean", "std"]
        a, g = grp["mean"].idxmin()
        return a, g, grp.loc[(a, g), "mean"], grp.loc[(a, g), "std"]
    # no summary: scan all grid files for this model (slow path)
    sub = index[(index.dataset == ds) & (index.regime == regime)
                & (index.model == model) & (index.alpha != "")]
    if len(sub) == 0:
        return None
    best = None
    for (a, g), rows in sub.groupby(["alpha", "gamma"]):
        t = tail_from_files(list(rows["file"]), args.tail)
        if best is None or t.mean() < best[2]:
            best = (a, g, t.mean(), t.std(ddof=0))
    return best


def model_tail(summary, index, ds, regime, model, args, alpha="", gamma=""):
    if summary is not None:
        sub = summary[(summary.dataset == ds) & (summary.regime == regime)
                      & (summary.model == model) & (summary.alpha == alpha)
                      & (summary.gamma == gamma)]
        if len(sub):
            return sub.overall_tail.mean(), sub.overall_tail.std(ddof=0)
    files, _ = config_files(index, ds, regime, model, alpha, gamma)
    if not files:
        return None, None
    t = tail_from_files(files, args.tail)
    return t.mean(), t.std(ddof=0)


# ================================================================
# House style helpers
# ================================================================
def plot_curve(ax, L, label, color, band=True):
    mean = np.mean(L, axis=0)
    std = np.std(L, axis=0)
    x = np.arange(len(mean))
    ax.plot(x, mean, label=label, color=color, lw=1.4)
    if band:
        ax.fill_between(x, np.maximum(mean - std, 1e-3), mean + std, color=color, alpha=0.15)


def save_fig(fig, args, stem):
    os.makedirs(args.fig_dir, exist_ok=True)
    for ext in args.formats:
        path = os.path.join(args.fig_dir, f"{args.prefix}{stem}.{ext}")
        fig.savefig(path, dpi=args.dpi if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {os.path.join(args.fig_dir, args.prefix + stem)}.{'/'.join(args.formats)}")


def resolve_shown_configs(summary, index, ds, regime, models, args):
    # -> list of (model, alpha_str, gamma_str, label_suffix)
    shown = []
    for m in MODELS_ORDER:
        if m not in models:
            continue
        if m in GRID_MODELS:
            bc = best_config(summary, index, ds, regime, m, args)
            if bc is None:
                continue
            a, g, _, _ = bc
            shown.append((m, a, g, f" (α={float(a):g}, γ={float(g):g})"))
        else:
            files, _ = config_files(index, ds, regime, m)
            if files:
                shown.append((m, "", "", ""))
    return shown


# ================================================================
# Figures
# ================================================================
def fig_overview(summary, index, ds, regime, args, labels, ylabels, xlabel):
    shown = resolve_shown_configs(summary, index, ds, regime,
                                  args.models or MODELS_ORDER, args)
    if not shown:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    tail_bits = []
    ref_curves = []
    for m, a, g, suff in shown:
        files, _ = config_files(index, ds, regime, m, a, g)
        if not files:
            continue
        L = stack_seed_curves(files, "overall")
        diverged = L.max() >= args.cap
        plot_curve(ax, L, labels[m] + suff, COL[m], band=not diverged)
        mu, sd = model_tail(summary, index, ds, regime, m, args, a, g)
        if mu is not None and mu < args.cap:
            tail_bits.append(f"{SHORT[m]} {mu:.4g}")
            ref_curves.append(np.mean(L, axis=0))
        if diverged:
            ax.annotate(f"{labels[m]} diverges (pinned at cap)", xy=(0.03, 0.96),
                        xycoords="axes fraction", va="top", fontsize=8, color=COL[m])
    if ref_curves:
        lo = 0.85 * min(c.min() for c in ref_curves)
        hi = 1.6 * max(np.median(c) for c in ref_curves)
        ax.set_ylim(lo, hi)
    ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabels[ds])
    n_seeds = len(config_files(index, ds, regime, shown[0][0],
                               shown[0][1], shown[0][2])[0])
    ax.set_title(f"{DS_LABEL[ds]}, {regime.upper()} regime, {n_seeds} seeds\n"
                 f"tail overall: " + ", ".join(tail_bits), fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, which="both")
    save_fig(fig, args, f"{ds}_{regime}_overview")


def fig_groups(summary, index, ds, regime, args, labels, ylabels, xlabel):
    shown = resolve_shown_configs(summary, index, ds, regime,
                                  args.models or MODELS_ORDER, args)
    if not shown:
        return
    # group column names from one file
    probe = config_files(index, ds, regime, shown[0][0], shown[0][1], shown[0][2])[0][0]
    gcols = [c for c in pd.read_csv(probe, nrows=1).columns if c.startswith("group_")]
    if not gcols:
        return
    curves = {}   # (model, gcol) -> (S, R)
    for m, a, g, suff in shown:
        files, _ = config_files(index, ds, regime, m, a, g)
        per_seed = [read_cols(f, gcols) for f in files]
        n = min(len(d) for d in per_seed)
        for gc in gcols:
            curves[(m, gc)] = np.stack([d[gc].values[:n] for d in per_seed])
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    for gi, gc in enumerate(gcols[:5]):
        ax = axes[gi // 3, gi % 3]
        for m, a, g, suff in shown:
            L = curves[(m, gc)]
            plot_curve(ax, L, labels[m], COL[m], band=L.max() < args.cap)
        ax.set_yscale("log")
        finite = [np.mean(curves[(m, gc)], axis=0) for m, *_ in shown
                  if curves[(m, gc)].max() < args.cap]
        if finite:
            ax.set_ylim(0.85 * min(c.min() for c in finite),
                        1.8 * max(np.median(c) for c in finite))
        ax.set_title(gc[len("group_"):], fontsize=10)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.grid(alpha=0.3, which="both")
        ax.tick_params(labelsize=8)
        if gi == 0:
            ax.legend(fontsize=7)
    # 6th panel: tail bars
    ax = axes[1, 2]
    xs = np.arange(len(gcols))
    live = [s for s in shown if max(curves[(s[0], gc)].max() for gc in gcols) < args.cap]
    wd = 0.8 / max(len(live), 1)
    for k, (m, a, g, suff) in enumerate(live):
        gt = [curves[(m, gc)][:, -args.tail:].mean() for gc in gcols]
        ax.bar(xs + (k - (len(live) - 1) / 2) * wd, gt, wd, color=COL[m], label=labels[m])
    ax.set_xticks(xs)
    ax.set_xticklabels([gc[len("group_"):].replace("-", "-\n") for gc in gcols], fontsize=7)
    ax.set_ylabel(f"tail-{args.tail} group loss", fontsize=8)
    ax.set_title("final per-group loss", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    grp_word = "critical groups" if args.vocab == "defed" else "critical groups"
    fig.suptitle(f"{DS_LABEL[ds]}, {regime.upper()} regime: loss per critical group",
                 fontsize=12)
    fig.tight_layout()
    save_fig(fig, args, f"{ds}_{regime}_groups")


def fig_users(summary, index, ds, regime, args, labels, xlabel):
    shown = resolve_shown_configs(summary, index, ds, regime,
                                  args.models or MODELS_ORDER, args)
    if not shown:
        return
    fig, axes = plt.subplots(len(shown), 1, figsize=(11, 2.2 * len(shown) + 1.5),
                             sharex=True)
    if len(shown) == 1:
        axes = [axes]
    ims = []
    for ax, (m, a, g, suff) in zip(axes, shown):
        files, _ = config_files(index, ds, regime, m, a, g)
        d = pd.read_csv(files[0])
        ucols = [c for c in d.columns if c.startswith("user_")]
        U = d[ucols].values           # (R, N), NaN on non-logged rounds
        rounds = d["round"].values
        logged = ~np.isnan(U).all(axis=1)
        U, rounds = U[logged], rounds[logged]
        stride = args.user_round_stride or max(1, len(rounds) // 1000)
        U, rounds = U[::stride], rounds[::stride]
        finite = U[np.isfinite(U) & (U < args.cap)]
        Umask = np.where(U >= args.cap, np.nan, U)
        with np.errstate(divide="ignore", invalid="ignore"):
            logU = np.log10(Umask)
        vmin, vmax = (np.nanpercentile(logU, [2, 98]) if finite.size else (0, 1))
        im = ax.imshow(logU.T, aspect="auto", origin="upper", cmap="viridis",
                       vmin=vmin, vmax=vmax,
                       extent=[rounds[0], rounds[-1], len(ucols), 0])
        ims.append(im)
        ax.set_ylabel("user (by p rank)", fontsize=8)
        ax.set_title(labels[m] + suff + " (seed 0)", fontsize=9, loc="left")
        ax.tick_params(labelsize=8)
    axes[-1].set_xlabel(xlabel)
    fig.colorbar(ims[0], ax=axes, fraction=0.02, pad=0.02, label="log10 loss")
    fig.suptitle(f"{DS_LABEL[ds]}, {regime.upper()} regime: per-user loss", fontsize=12)
    save_fig(fig, args, f"{ds}_{regime}_users")


def fig_heatmaps(summary, index, ds, regime, args, labels):
    if summary is None:
        print("  heatmaps need summary.csv (run run_experiments.py --rebuild-summary)")
        return
    for m in GRID_MODELS:
        if args.models and m not in args.models:
            continue
        sub = summary[(summary.dataset == ds) & (summary.regime == regime)
                      & (summary.model == m) & (summary.alpha != "")]
        if len(sub) == 0:
            continue
        alphas = sorted(sub.alpha.unique(), key=float)
        gammas = sorted(sub.gamma.unique(), key=float)
        Ho = np.full((len(gammas), len(alphas)), np.nan)
        Hw = np.full_like(Ho, np.nan)
        Div = np.zeros_like(Ho, dtype=bool)
        for (a, g), rows in sub.groupby(["alpha", "gamma"]):
            yi, xi = gammas.index(g), alphas.index(a)
            if rows.diverged.max() > 0:
                Div[yi, xi] = True
            else:
                Ho[yi, xi] = rows.overall_tail.mean()
                Hw[yi, xi] = rows.worst_group_tail.mean()
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))
        for ax, H, name in ((axs[0], Ho, "tail overall"), (axs[1], Hw, "tail worst-group")):
            cmap = plt.get_cmap("viridis").copy()
            cmap.set_bad("lightgray")
            im = ax.imshow(H, origin="lower", cmap=cmap, aspect="auto")
            ax.set_xticks(range(len(alphas)))
            ax.set_xticklabels([f"{float(a):g}" for a in alphas], fontsize=7)
            ax.set_yticks(range(len(gammas)))
            ax.set_yticklabels([f"{float(g):g}" for g in gammas], fontsize=7)
            ax.set_xlabel("α")
            ax.set_ylabel("γ")
            if np.isfinite(H).any():
                by, bx = np.unravel_index(np.nanargmin(H), H.shape)
                ax.plot(bx, by, marker="*", color="red", ms=14, mec="white")
            for yi in range(len(gammas)):
                for xi in range(len(alphas)):
                    if Div[yi, xi]:
                        ax.text(xi, yi, "DIV", ha="center", va="center",
                                fontsize=6, color="red")
                    elif not args.no_annot and np.isfinite(H[yi, xi]):
                        ax.text(xi, yi, f"{H[yi, xi]:.4g}", ha="center", va="center",
                                fontsize=5.5, color="white")
            ax.set_title(name, fontsize=10)
            fig.colorbar(im, ax=ax, fraction=0.046)
        fig.suptitle(f"{DS_LABEL[ds]}, {regime.upper()}: {labels[m]} over (α, γ) "
                     f"(mean over seeds; ★ = best; γ=1 row must match "
                     f"{labels['fedavot' if m == 'fedavot_cvar' else 'fedavg']})",
                     fontsize=10)
        fig.tight_layout()
        save_fig(fig, args, f"{ds}_{regime}_{m}_heatmap")


def best_table(summary, index, args, labels):
    rows = []
    datasets = args.datasets or sorted(index.dataset.unique())
    regimes = args.regimes or sorted(index.regime.unique())
    for ds in datasets:
        for regime in regimes:
            for m in MODELS_ORDER:
                if args.models and m not in args.models:
                    continue
                if m in GRID_MODELS:
                    bc = best_config(summary, index, ds, regime, m, args)
                    if bc is None:
                        continue
                    a, g, mu, sd = bc
                else:
                    a, g = "", ""
                    mu, sd = model_tail(summary, index, ds, regime, m, args)
                    if mu is None:
                        continue
                rows.append(dict(dataset=ds, regime=regime, model=m,
                                 alpha=a, gamma=g,
                                 overall_tail_mean=f"{mu:.6g}",
                                 overall_tail_std=f"{sd:.3g}" if sd == sd else ""))
    if not rows:
        return
    df = pd.DataFrame(rows)
    print("\n=== best configurations (tail overall, mean ± std over seeds) ===")
    for _, r in df.iterrows():
        ag = f"  (α={float(r.alpha):g}, γ={float(r.gamma):g})" if r.alpha else ""
        print(f"  {r.dataset:9s} {r.regime:10s} {labels[r.model]:26s}{ag:18s} "
              f"{r.overall_tail_mean} ± {r.overall_tail_std}")
    os.makedirs(args.fig_dir, exist_ok=True)
    out = os.path.join(args.fig_dir, f"{args.prefix}best_table.csv")
    df.to_csv(out, index=False)
    print(f"wrote {out}")


# ================================================================
# Main
# ================================================================
def main(argv=None):
    args = parse_args(argv)
    index = index_files(args.results_dir)
    summary = load_summary(args.results_dir)
    if summary is None:
        print(f"note: no summary.csv in {args.results_dir}; tail stats recomputed from "
              f"curves (slow). Run run_experiments.py --rebuild-summary to create it.")
    labels = LBL_DEFED if args.vocab == "defed" else LBL_FL
    ylabels = YLABEL_DEFED if args.vocab == "defed" else YLABEL_FL
    xlabel = "Iteration" if args.vocab == "defed" else "Round"

    datasets = args.datasets or sorted(index.dataset.unique())
    regimes = args.regimes or sorted(index.regime.unique())
    for ds in datasets:
        for regime in regimes:
            if len(index[(index.dataset == ds) & (index.regime == regime)]) == 0:
                continue
            print(f"--- {ds} / {regime} ---")
            if "overview" in args.figures:
                fig_overview(summary, index, ds, regime, args, labels, ylabels, xlabel)
            if "groups" in args.figures:
                fig_groups(summary, index, ds, regime, args, labels, ylabels, xlabel)
            if "users" in args.figures:
                fig_users(summary, index, ds, regime, args, labels, xlabel)
            if "heatmaps" in args.figures:
                fig_heatmaps(summary, index, ds, regime, args, labels)
    if "best-table" in args.figures:
        best_table(summary, index, args, labels)


if __name__ == "__main__":
    main()
