# sheets_export

Curated CSVs for the **Google Sheets deliverable** (2026-08-10), cut down from the raw
sweep in `results/2026-08-10_main_sweep/`. Also the input for
`scripts/metric_summary_figures.py`.

| File | Contents |
|---|---|
| `{adult,imdbwiki}_{feasible,infeasible}_overall.csv` | Per-round overall loss curves, one column per algorithm: `round, FedAVOT, FedAVOT + CVaR (a=0.3, g=0.3), FedCVaR uniform agg (a=0.3, g=0.3), FedAvg (uniform over K), FedAvg (full)` |
| `group_tails.csv` | Tail-500 loss per critical group (Adult: 5 races; IMDb-Wiki: importance quintiles tier1–5) for the same five algorithms |
| `best_table.csv` | Overall tail-500 mean ± std per (dataset, regime, model, α, γ) — the best-config selection table |

Note: the CVaR columns here are pinned at **(α, γ) = (0.3, 0.3)** (the Sheets-era
convention). The per-cell *tuned* configs used in later deliverables are documented in
`results/2026-08-15_herlock_core_metrics/`.
