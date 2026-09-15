#!/usr/bin/env bash
# Assemble the four 2026-09-14 paper cells (LR decay; grid-free models + fixed multiplier + the
# full CVaR grid) into ONE results dir in the layout plot_experiments.py expects, rebuild its
# summary.csv, and regenerate the 8/30-package figure set with the de-federated vocabulary.
#   imdb_beta0.00_decay1000   -> imdbwiki_infeasible_*   (uniform availability, the paper's infeasible panel)
#   imdb_feasible_decay1000   -> imdbwiki_feasible_*
#   adult_beta0.00_decay1000  -> adult_infeasible_*       (prevalence availability)
#   adult_beta1.00_decay1000  -> adult_feasible_*         (aligned; run under --regimes infeasible --r-power 1, so RENAMED)
# Usage (repo root): bash scripts/pipeline/build_paper_package.sh
set -eu
P=.venv/Scripts/python.exe
SRC=results/2026-09-14_severity_sweep
DST=results/2026-09-15_paper_cells
FIG=figures/2026-09-15_paper_package
rm -rf "$DST"; mkdir -p "$DST"
cp "$SRC"/imdb_beta0.00_decay1000/imdbwiki_infeasible_*.csv.gz "$DST"/
cp "$SRC"/imdb_feasible_decay1000/imdbwiki_feasible_*.csv.gz "$DST"/
cp "$SRC"/adult_beta0.00_decay1000/adult_infeasible_*.csv.gz "$DST"/
for f in "$SRC"/adult_beta1.00_decay1000/adult_infeasible_*.csv.gz; do
  cp "$f" "$DST/$(basename "$f" | sed 's/^adult_infeasible_/adult_feasible_/')"
done
echo "$(ls "$DST" | wc -l) run files staged in $DST"
$P scripts/pipeline/run_experiments.py --rebuild-summary --outdir "$DST" --gzip --lr-decay 1000 --rounds 4000
PYTHONIOENCODING=utf-8 $P scripts/pipeline/plot_experiments.py --results-dir "$DST" --fig-dir "$FIG" --vocab defed --prefix paper_
echo "figures in $FIG"
