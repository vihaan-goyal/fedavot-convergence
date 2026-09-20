# Imbalance baselines and the Adult 16k check, 2026-09-20

Herlock (9/20): "comparing with baselines like up and down sampling and imbalanced regression".
Runs: `results/2026-09-20_baselines/<cell>/` (models `ipw`, `downsample`, 5 seeds, decay 1000,
4000 steps, same flags as the severity sweep); Adult 16k: `results/2026-09-20_adult_16k/`;
IMDb feasible at constant stepsize: `results/2026-09-14_severity_sweep/imdb_feasible_const/`
(now in `severity_sweep_table.csv`). Runner: `scripts/pipeline/run_experiments.py`, commit fd4ef5c.

## What the two baselines are (both convex, self-normalized over the K observed groups)

- **upsample** (`ipw`): weight group i by its under-observation ratio p_i / pi_i, renormalized
  within the batch. The reweighting form of oversampling rare groups; cannot diverge, unlike
  the fixed multiplier (N/K) p_i, which is the un-normalized version.
- **downsample**: weight by min(p_i / pi_i, 1), renormalized: over-observed (majority) groups are
  down-weighted, starved groups left at their share.
- Upsampling as a *sampler* change is already the beta axis of the sweep: beta = 1 on Adult is
  "observe in proportion to importance", and group-blind averaging there (0.2077) is the
  perfectly-upsampled baseline. The coverage law p_i <= r_i is where sampler upsampling stops.

## Results, decaying stepsize, tail-500 over 5 seeds

Overall objective (CE on Adult, MSE on IMDb):

| Instance | GAVOT | group-blind | upsample | downsample | full |
|---|---|---|---|---|---|
| Adult prevalence (nu=.60) | **0.2269** | 0.2479 | 0.2288 | 0.2308 | 0.2073 |
| Adult aligned (nu=0) | 0.2075 | 0.2077 | 0.2075 | 0.2075 | 0.2073 |
| IMDb skewed (nu=.31) | **86.06** | 91.63 | 86.74 | 86.90 | 82.95 |
| IMDb aligned (nu=0) | **84.28** | 86.37 | 84.40 | 84.40 | 82.95 |

Least represented group (race Other on Adult; top-importance identities on IMDb):

| Instance | GAVOT | group-blind | upsample | downsample | full |
|---|---|---|---|---|---|
| Adult prevalence | **.0732** | .1194 | .0746 | .0805 | .0309 |
| Adult aligned | **.0318** | .0352 | .0325 | .0325 | .0309 |
| IMDb skewed | **76.99** | 86.42 | 79.95 | 80.23 | 72.23 |
| IMDb aligned | **73.63** | 79.89 | 75.59 | 75.59 | 72.23 |

Reading: self-normalized upsampling is a strong baseline, far ahead of group-blind averaging and
within 0.002 CE / 0.7 MSE of transport on the overall objective. Transport is ahead on every
instance, and by more on the rare group (3 MSE on IMDb skewed, 2 on IMDb aligned). The two are
the same idea at different precision: upsampling is the one-shot heuristic (ratio weights,
normalized per batch), transport is the exact solution of the same marginal problem, with the
feasibility certificate and the floor decomposition attached. Downsampling is never better than
upsampling. On the aligned instances all convex rules tie, as Prop. 2 predicts.

Where this goes: two more columns in Table 1 (or a small table in the extended version) and one
sentence in E1: "self-normalized upsampling recovers most of the gain and transport the rest;
the un-normalized version is the fixed multiplier, which diverges."

## Adult 16k check (decay, tail-500 of 16000 vs 4000)

| beta | nu | gain at 4k | gain at 16k | Delta_floor | GAVOT 16k | full 16k |
|---|---|---|---|---|---|---|
| 0 | .60 | +.0210 | +.0171 | .0110 | .2229 | .2047 |
| 0.25 | .60 | +.0181 | +.0161 | .0144 | .2119 | .2047 |
| 0.5 | .40 | +.0134 | +.0130 | .0129 | .2049 | .2047 |
| 0.75 | 0 | +.0050 | +.0047 | .0049 | .2047 | .2047 |
| 1 | 0 | +.0002 | +.0001 | .0003 | .2047 | .2047 |

Every rule, full coverage included, is still descending at 16000 rounds under eta/(1+t/1000)
(full: .2073 -> .2047, floor .1993), so the offset is common to all rules and the comparison
against measured full is fair at any T. The measured gains drift toward Delta_floor with T; at
16k three of five are within 4% and the two most infeasible are still above. GAVOT matches full
to four decimals at beta >= 0.5 by 16k. Decision: keep the 4000-step numbers in the paper
(consistent with IMDb), state "at 4000 steps", and note that the Adult gains exceeding
Delta_floor at beta = 0 and 0.25 shrink toward it with T (E3 wording).

## IMDb feasible at constant stepsize (the previously blank cell)

GAVOT 89.08 +- 0.53, group-blind 89.51 +- 0.55, full 83.07: a near tie at constant stepsize,
same pattern as the infeasible cell (variance masks the floor gap of 2.7); with decay 84.28 vs
86.37.
