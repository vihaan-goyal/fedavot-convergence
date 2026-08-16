# Figures

Organized into dated per-experiment subfolders. The date is when that batch of figures
was (re)generated; scripts save into their own folder, so reruns overwrite in place.

| Folder | Contents | Produced by |
|---|---|---|
| `2026-07-08_notebook_legacy/` | Early linreg / MNIST K=2 comparison figures | `scripts/legacy/lin_reg_last_one.py`, `scripts/legacy/icasp2025.py` (notebook era) |
| `2026-07-11_feasible_5k/` | Phase-boundary feasible panel (alpha=0.5) at 5000 rounds | `scripts/paper_experiments/synthetic/feasible_5k_rounds.py` |
| `2026-07-11_cvar_study/` | FED-CVaR-AVG x FedAVOT study on IMDb-Wiki (`imdbwiki_cvar_*`): infeasible/feasible, (alpha,gamma) grid, a=0.9 bookends, alpha trend | `scripts/cvar_study/runs/imdbwiki_cvar_*.py`, `scripts/cvar_study/cvar_alpha_trend.py` |
| `2026-07-15_regularized_transport/` | Lambda-penalized (unbalanced) masked Sinkhorn sweep | `scripts/paper_experiments/theory_checks/regularized_transport_sweep.py` |
| `2026-07-27_ram_study/` | Restricted-availability (RAM) setting of arXiv:2309.14176: feasibility diagnostic, CVaR-vs-FedAVOT training, metric disagreement | `scripts/ram_study/ram_feasibility_diagnostic.py`, `scripts/ram_study/ram_cvar_vs_fedavot.py`, `scripts/ram_study/ram_replot.py` |
| `2026-07-27_paper/` | **The paper figures** (Overleaf uploads): mechanism, phase boundary, IMDb-Wiki infeasible/feasible, Adult fairness. De-federated vocabulary as of 2026-07-27 | `scripts/paper_experiments/synthetic/feasibility_diagnostic.py`, `scripts/paper_experiments/synthetic/phase_boundary_experiment.py`, `scripts/paper_experiments/imdbwiki/imdbwiki_infeasible_4k.py`, `scripts/paper_experiments/imdbwiki/imdbwiki_feasible_5k.py`, `scripts/paper_experiments/adult/adult_fairness.py`, `scripts/paper_experiments/replot_paper_figures.py` |
| `2026-08-10_sweep_pipeline/` | Unified argparse pipeline outputs (`exp_*`), in subfolders `best_config/` (overview / groups / users at each model's best config), `pinned_a03g03/` (same three at (alpha,gamma)=(0.3,0.3)), `heatmaps/` ((alpha,gamma) grids); `exp_best_table.csv` at the root. `save_fig` routes reruns into the same subfolders | `scripts/pipeline/plot_experiments.py` (default `--fig-dir` points here) |
| `2026-08-14_metric_summary/` | Discord-facing summaries of the sweep metric tables: severity-inversion bars (FedAVOT vs uniform, normalized to full) and standalone per-critical-group tail bars | `scripts/pipeline/metric_summary_figures.py` (reads `sheets_export/*.csv`, no retraining) |

`paper/preview.tex`'s `\graphicspath` includes `2026-07-27_paper/`, so the tex fragments
reference the paper PDFs by bare filename as before.
