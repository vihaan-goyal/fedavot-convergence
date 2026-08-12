# Figures

Organized into dated per-experiment subfolders. The date is when that batch of figures
was (re)generated; scripts save into their own folder, so reruns overwrite in place.

| Folder | Contents | Produced by |
|---|---|---|
| `2026-07-08_notebook_legacy/` | Early linreg / MNIST K=2 comparison figures | `scripts/lin_reg_last_one.py`, `scripts/icasp2025.py` (notebook era) |
| `2026-07-11_feasible_5k/` | Phase-boundary feasible panel (alpha=0.5) at 5000 rounds | `scripts/feasible_5k_rounds.py` |
| `2026-07-11_cvar_study/` | FED-CVaR-AVG x FedAVOT study on IMDb-Wiki (`imdbwiki_cvar_*`): infeasible/feasible, (alpha,gamma) grid, a=0.9 bookends, alpha trend | `scripts/imdbwiki_cvar_*.py`, `scripts/cvar_alpha_trend.py` |
| `2026-07-15_regularized_transport/` | Lambda-penalized (unbalanced) masked Sinkhorn sweep | `scripts/regularized_transport_sweep.py` |
| `2026-07-27_ram_study/` | Restricted-availability (RAM) setting of arXiv:2309.14176: feasibility diagnostic, CVaR-vs-FedAVOT training, metric disagreement | `scripts/ram_feasibility_diagnostic.py`, `scripts/ram_cvar_vs_fedavot.py`, `scripts/ram_replot.py` |
| `2026-07-27_paper/` | **The paper figures** (Overleaf uploads): mechanism, phase boundary, IMDb-Wiki infeasible/feasible, Adult fairness. De-federated vocabulary as of 2026-07-27 | `scripts/feasibility_diagnostic.py`, `scripts/phase_boundary_experiment.py`, `scripts/imdbwiki_infeasible_4k.py`, `scripts/imdbwiki_feasible_5k.py`, `scripts/adult_fairness.py`, `scripts/replot_paper_figures.py` |
| `2026-08-10_sweep_pipeline/` | Unified argparse pipeline outputs (`exp_*`): overview / groups / users / heatmaps per dataset x regime, pinned (0.3,0.3) variants, `exp_best_table.csv` | `scripts/plot_experiments.py` (default `--fig-dir` points here) |

`paper/preview.tex`'s `\graphicspath` includes `2026-07-27_paper/`, so the tex fragments
reference the paper PDFs by bare filename as before.
