# Scripts

Organized by study. Every script still runs **from the repo root** (all data/figure paths
inside them are root-relative):

```powershell
.venv/Scripts/python.exe scripts/<subfolder>/<name>.py
```

Knobs live in an ALL-CAPS config block at the top of each script — there is **no CLI**,
except the two `pipeline/` scripts, which are argparse-driven by design. Most scripts save
raw loss curves to `data/*_curves.npz` so figures can be replotted without retraining.

```
scripts/
├── pipeline/            the unified sweep pipeline (the only CLI scripts)
├── paper_experiments/   the ICASSP paper's experiments
│   ├── synthetic/       mechanism + phase-boundary (no real data)
│   ├── imdbwiki/        the real-data IMDb-Wiki cells
│   ├── adult/           the Adult (Census) fairness cell
│   └── theory_checks/   no-training / theory-bridge analyses
├── cvar_study/          FED-CVaR-AVG x FedAVOT study (arXiv:2309.14176)
│   └── runs/            the training runs; summary figure at cvar_study/ root
├── ram_study/           their paper's own restricted-availability MNIST setting
└── legacy/              early standalone snapshots
```

## pipeline/

| Script | What it does |
|---|---|
| `run_experiments.py` | Trains 4 models (fedavot, fedavot_cvar, fedcvar, fedavg) × {feasible, infeasible} × (α, γ) grid × {imdbwiki, adult} + full-participation reference. One wide CSV per config × seed → `results/<date>_<desc>/`. `--smoke` for a 1-minute check, `--selftest` for the engine identity checks |
| `plot_experiments.py` | All figures from the run CSVs (no retraining): overview / per-group / per-user / (α, γ) heatmaps / best-table → `figures/2026-08-10_sweep_pipeline/{best_config,pinned_a03g03,heatmaps}/` |
| `metric_summary_figures.py` | Discord-facing severity-inversion + per-group tail bars from `sheets_export/*.csv` |

## paper_experiments/

| Script | What it does |
|---|---|
| `synthetic/feasibility_diagnostic.py` | The mechanism figure: achieved vs target weight with the π ceiling; IPFP row errors |
| `synthetic/phase_boundary_experiment.py` | Synthetic α sweep: feasible/infeasible loss panels + phase boundary |
| `synthetic/feasible_5k_rounds.py` | Phase-boundary feasible panel (α=0.5) at 5000 rounds |
| `imdbwiki/imdbwiki_infeasible_4k.py` | IMDb-Wiki mirrored p/r (INFEASIBLE) — the paper's main real-data cell |
| `imdbwiki/imdbwiki_feasible_5k.py` | IMDb-Wiki with availability aligned to importance (FEASIBLE); FedAvg(K) diverges here |
| `adult/adult_fairness.py` | Adult (Census) race-fairness experiment, both regimes in one figure |
| `theory_checks/infeasible_bias_check.py` | No training: stalled-IPFP surrogate marginal + closed-form optima → Sec 3.3 bias bound |
| `theory_checks/regularized_transport_sweep.py` | λ-penalized (unbalanced) masked Sinkhorn sweep — λ tunes variance, not bias |
| `replot_paper_figures.py` | Regenerates the curve-based paper figures from saved npz with the de-federated vocabulary |

## cvar_study/  (FED-CVaR-AVG × FedAVOT, arXiv:2309.14176)

| Script | What it does |
|---|---|
| `runs/imdbwiki_cvar_fedavot.py` | Infeasible regime, α=0.3 |
| `runs/imdbwiki_cvar_feasible.py` | Feasible (aligned) regime |
| `runs/imdbwiki_cvar_grid.py` | (α, γ) grid + hinge-tilted-aggregation variant |
| `runs/imdbwiki_cvar_a09_infeasible.py` / `_a09_feasible.py` | Near-risk-neutral (α=0.9) bookends |
| `cvar_alpha_trend.py` | Summary figure from the saved npz |

## ram_study/  (their paper's own restricted-availability setting)

| Script | What it does |
|---|---|
| `ram_feasibility_diagnostic.py` | Transport geometry of the arXiv:2309.14176 MNIST setting; sweeps users-per-round R; introduces the enumeration-free transport solver (`--validate`) |
| `ram_cvar_vs_fedavot.py` | The training experiment: 5 rules × R ∈ {1,3,6} × 3 (α,γ), 1500 rounds (`--smoke` available) |
| `ram_replot.py` | Replots the RAM figures from `data/ram_*.npz` |
| `prep_mnist_cache.py` | One-off MNIST fetch → `data/mnist_cache.npz` (git-ignored) |

## legacy/

| Script | What it does |
|---|---|
| `icasp2025.py` | Early standalone MNIST snapshot (notebook era) |
| `lin_reg_last_one.py` | Early synthetic linear-regression snapshot |

Also: `results/2026-08-15_herlock_core_metrics/make_core_metrics.py` regenerates that
deliverable from the sweep CSVs (kept next to its outputs).
