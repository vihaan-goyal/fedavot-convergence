# Results

Convention: **one dated `results/<YYYY-MM-DD>_<desc>/` folder per run or analysis.**
Raw sweep run folders are git-ignored (they run to ~15 GB); small *derived* analysis
folders are re-included explicitly in `.gitignore` and committed.

| Folder | What it is | In git? |
|---|---|---|
| `2026-08-10_main_sweep/` | The completed full sweep from `scripts/pipeline/run_experiments.py`: 4 models × {imdbwiki, adult} × {feasible, infeasible} × 10×10 (α, γ) grid × 5 seeds × 4000 rounds. One gzipped wide CSV per config × seed (`round, overall, group_* ×5, user_0..99` — per-user losses logged **every round**) plus `summary.csv` (per-seed tail stats incl. `worst_group_tail`) | **No** (ignored; local + on Vihaan's other machine) |
| `2026-08-14_worst_group_vs_baseline/` | `beats_baseline.csv`: all 354 grid configs whose worst-group tail-500 loss beats the plain FedAVOT / uniform-K baseline, with margins | Yes |
| `2026-08-15_herlock_core_metrics/` | The tiered deliverable: overall point-ranges, sorted per-client curves, per-group regret heatmaps (+ CSVs), bonus Adult per-client-over-time heatmaps, `core_metrics_report.html` (self-contained, shareable), and `make_core_metrics.py` to regenerate it all from the sweep CSVs | Yes |

FOOTGUN (from `run_experiments.py`): output filenames omit the round count — runs at a
non-default `--rounds` need their own `--outdir` or they silently overwrite the sweep.

Curated per-round CSVs for the Google Sheets deliverable live in `../sheets_export/`.
