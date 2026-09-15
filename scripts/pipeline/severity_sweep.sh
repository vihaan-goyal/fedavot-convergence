#!/usr/bin/env bash
# Infeasibility-severity sweep (Herlock's 2026-09-14 ask: "make runs to make it do better" on the
# infeasible cases). Grid-free models only (fedavot, fedavg = uniform-over-K, full), 5 seeds,
# 4000 rounds, with and without learning-rate decay. One outdir per cell (filenames omit the knobs).
#   imdbwiki: --r-power beta in {0 .. 3}: r ~ i^beta, 3 = the paper's mirrored-cubic anchor
#   adult:    --r-power beta in {0 .. 1}: r ~ p^beta, 0 = the paper's uniform anchor
# Usage (repo root):  bash scripts/pipeline/severity_sweep.sh [jobs]
set -u
P=.venv/Scripts/python.exe
ROOT=results/2026-09-14_severity_sweep
JOBS=${1:-6}
COMMON="--models fedavot fedavg full --seeds 0 1 2 3 4 --sweep --gzip --user-log-every 10 --progress-every 0 --no-clobber"
mkdir -p "$ROOT/logs"
jobs=()
for decay in 1000 none; do
  d=""; tag="const"; [ "$decay" != none ] && { d="--lr-decay $decay"; tag="decay$decay"; }
  for b in 0.00 0.50 1.00 1.50 2.00 3.00; do
    jobs+=("$P scripts/pipeline/run_experiments.py --datasets imdbwiki --regimes infeasible --r-power $b $d $COMMON --outdir $ROOT/imdb_beta${b}_$tag > $ROOT/logs/imdb_beta${b}_$tag.log 2>&1; echo CELL_DONE imdb_beta${b}_$tag >> $ROOT/logs/done.txt")
  done
  for b in 0.00 0.25 0.50 0.75 1.00; do
    jobs+=("$P scripts/pipeline/run_experiments.py --datasets adult --regimes infeasible --r-power $b $d $COMMON --outdir $ROOT/adult_beta${b}_$tag > $ROOT/logs/adult_beta${b}_$tag.log 2>&1; echo CELL_DONE adult_beta${b}_$tag >> $ROOT/logs/done.txt")
  done
done
jobs+=("$P scripts/pipeline/run_experiments.py --datasets imdbwiki --regimes feasible --lr-decay 1000 $COMMON --outdir $ROOT/imdb_feasible_decay1000 > $ROOT/logs/imdb_feasible_decay1000.log 2>&1; echo CELL_DONE imdb_feasible_decay1000 >> $ROOT/logs/done.txt")
printf '%s\n' "${jobs[@]}" > "$ROOT/logs/joblist.txt"
echo "${#jobs[@]} cells, $JOBS parallel"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
printf '%s\n' "${jobs[@]}" | xargs -P "$JOBS" -I{} bash -c '{}'
echo SWEEP_DONE
