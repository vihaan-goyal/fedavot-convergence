# Scripts

Every script runs **from the repo root** (all paths are root-relative):

```powershell
.venv/Scripts/python.exe scripts/<name>.py
```

Knobs live in an ALL-CAPS config block at the top of each script — there is **no CLI**,
except `run_experiments.py` / `plot_experiments.py`, which are argparse-driven by design.
Most scripts save raw loss curves to `data/*_curves.npz` so figures can be replotted
without retraining.

## The unified sweep pipeline (the only CLI scripts)

| Script | What it does |
|---|---|
| `run_experiments.py` | Trains 4 models (fedavot, fedavot_cvar, fedcvar, fedavg) × {feasible, infeasible} × (α, γ) grid × {imdbwiki, adult} + full-participation reference. One wide CSV per config × seed → `results/<date>_<desc>/`. `--smoke` for a 1-minute check, `--selftest` for the engine identity checks |
| `plot_experiments.py` | All figures from the run CSVs (no retraining): overview / per-group / per-user / (α, γ) heatmaps / best-table → `figures/2026-08-10_sweep_pipeline/{best_config,pinned_a03g03,heatmaps}/` |

## Paper experiments (2026-07)

| Script | What it does |
|---|---|
| `feasibility_diagnostic.py` | The mechanism figure: achieved vs target weight with the π ceiling; IPFP row errors |
| `phase_boundary_experiment.py` | Synthetic α sweep: feasible/infeasible loss panels + phase boundary |
| `feasible_5k_rounds.py` | Phase-boundary feasible panel (α=0.5) at 5000 rounds |
| `imdbwiki_infeasible_4k.py` | IMDb-Wiki mirrored p/r (INFEASIBLE) — the paper's main real-data cell |
| `imdbwiki_feasible_5k.py` | IMDb-Wiki with availability aligned to importance (FEASIBLE); FedAvg(K) diverges here |
| `adult_fairness.py` | Adult (Census) race-fairness experiment, both regimes in one figure |
| `infeasible_bias_check.py` | No training: stalled-IPFP surrogate marginal + closed-form optima → Sec 3.3 bias bound |
| `regularized_transport_sweep.py` | λ-penalized (unbalanced) masked Sinkhorn sweep — λ tunes variance, not bias |
| `replot_paper_figures.py` | Regenerates the curve-based paper figures from saved npz with the de-federated vocabulary |

## CVaR study (FED-CVaR-AVG × FedAVOT, arXiv:2309.14176)

| Script | What it does |
|---|---|
| `imdbwiki_cvar_fedavot.py` | Infeasible regime, α=0.3 |
| `imdbwiki_cvar_feasible.py` | Feasible (aligned) regime |
| `imdbwiki_cvar_grid.py` | (α, γ) grid + hinge-tilted-aggregation variant |
| `imdbwiki_cvar_a09_infeasible.py` / `_a09_feasible.py` | Near-risk-neutral (α=0.9) bookends |
| `cvar_alpha_trend.py` | Summary figure from the saved npz |

## RAM study (their paper's own restricted-availability setting)

| Script | What it does |
|---|---|
| `ram_feasibility_diagnostic.py` | Transport geometry of the arXiv:2309.14176 MNIST setting; sweeps users-per-round R; introduces the enumeration-free transport solver (`--validate`) |
| `ram_cvar_vs_fedavot.py` | The training experiment: 5 rules × R ∈ {1,3,6} × 3 (α,γ), 1500 rounds (`--smoke` available) |
| `ram_replot.py` | Replots the RAM figures from `data/ram_*.npz` |

## Summaries & utilities

| Script | What it does |
|---|---|
| `metric_summary_figures.py` | Discord-facing severity-inversion + per-group tail bars from `sheets_export/*.csv` |
| `prep_mnist_cache.py` | One-off MNIST fetch → `data/mnist_cache.npz` (git-ignored) |
| `icasp2025.py`, `lin_reg_last_one.py` | Early standalone snapshots (MNIST / synthetic linear regression) |

Also: `results/2026-08-15_herlock_core_metrics/make_core_metrics.py` regenerates that
deliverable from the sweep CSVs (kept next to its outputs).
