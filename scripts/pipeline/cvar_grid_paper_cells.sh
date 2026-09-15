#!/usr/bin/env bash
# Full (alpha, gamma) 10x10 CVaR grid (fedavot_cvar, fedcvar) on the four 2026-09-14 paper cells,
# LR decay 1000, 5 seeds, written into the same cell folders (--no-clobber keeps the grid-free runs).
set -u
P=.venv/Scripts/python.exe
R=results/2026-09-14_severity_sweep
C="--models fedavot_cvar fedcvar --seeds 0 1 2 3 4 --sweep --gzip --user-log-every 10 --progress-every 0 --no-clobber --lr-decay 1000"
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3
rm -f $R/logs/cvar_done.txt
( $P scripts/pipeline/run_experiments.py --datasets imdbwiki --regimes infeasible --r-power 0 $C --outdir $R/imdb_beta0.00_decay1000 > $R/logs/cvar_imdb_beta0.00_decay1000.log 2>&1; echo imdb_beta0.00_decay1000 >> $R/logs/cvar_done.txt ) &
( $P scripts/pipeline/run_experiments.py --datasets imdbwiki --regimes feasible $C --outdir $R/imdb_feasible_decay1000 > $R/logs/cvar_imdb_feasible_decay1000.log 2>&1; echo imdb_feasible_decay1000 >> $R/logs/cvar_done.txt ) &
( $P scripts/pipeline/run_experiments.py --datasets adult --regimes infeasible --r-power 0 $C --outdir $R/adult_beta0.00_decay1000 > $R/logs/cvar_adult_beta0.00_decay1000.log 2>&1; echo adult_beta0.00_decay1000 >> $R/logs/cvar_done.txt ) &
( $P scripts/pipeline/run_experiments.py --datasets adult --regimes infeasible --r-power 1 $C --outdir $R/adult_beta1.00_decay1000 > $R/logs/cvar_adult_beta1.00_decay1000.log 2>&1; echo adult_beta1.00_decay1000 >> $R/logs/cvar_done.txt ) &
wait
echo CVAR_GRID_DONE
