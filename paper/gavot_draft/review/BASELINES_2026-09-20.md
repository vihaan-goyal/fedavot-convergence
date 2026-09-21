# Imbalance baselines and the Adult 16k check, 2026-09-20

Herlock (9/20): "comparing with baselines like up and down sampling and imbalanced regression".
Runs: `results/2026-09-20_baselines/<cell>/` (models `ipw`, `downsample`, `lds` (IMDb only), 5 seeds, decay 1000,
4000 steps, same flags as the severity sweep); Adult 16k: `results/2026-09-20_adult_16k/`;
IMDb feasible at constant stepsize: `results/2026-09-14_severity_sweep/imdb_feasible_const/`
(now in `severity_sweep_table.csv`). Runner: `scripts/pipeline/run_experiments.py`, commits fd4ef5c (ipw/downsample) and 4fa5541 (lds).

## What the two baselines are (both convex, self-normalized over the K observed groups)

- **upsample** (`ipw`): weight group i by its under-observation ratio p_i / pi_i, renormalized
  within the batch. The reweighting form of oversampling rare groups; cannot diverge, unlike
  the fixed multiplier (N/K) p_i, which is the un-normalized version.
- **downsample**: weight by min(p_i / pi_i, 1), renormalized: over-observed (majority) groups are
  down-weighted, starved groups left at their share.
- **LDS** (`lds`, imbalanced regression; Yang et al., "Delving into Deep Imbalanced Regression", ICML
  2021, https://dir.csail.mit.edu/): label distribution smoothing. Histogram of the target (age) in
  unit bins, Gaussian kernel (size 5, sigma 2), weight = inverse smoothed density normalized to
  mean 1; applied at the group level (mean weight of the group's samples), renormalized within
  the batch. Regression only, so IMDb only; Adult is classification (their FDS/LDS do not apply).
- Upsampling as a *sampler* change is already the beta axis of the sweep: beta = 1 on Adult is
  "observe in proportion to importance", and group-blind averaging there (0.2077) is the
  perfectly-upsampled baseline. The coverage law p_i <= r_i is where sampler upsampling stops.

## Results, decaying stepsize, tail-500 over 5 seeds

Overall objective (CE on Adult, MSE on IMDb):

| Instance | GAVOT | group-blind | upsample | downsample | LDS | full |
|---|---|---|---|---|---|---|
| Adult prevalence (nu=.60) | **0.2269** | 0.2479 | 0.2288 | 0.2308 | n/a | 0.2073 |
| Adult aligned (nu=0) | 0.2075 | 0.2077 | 0.2075 | 0.2075 | n/a | 0.2073 |
| IMDb skewed (nu=.31) | **86.06** | 91.63 | 86.74 | 86.90 | 94.28 | 82.95 |
| IMDb aligned (nu=0) | **84.28** | 86.37 | 84.40 | 84.40 | 89.43 | 82.95 |

Least represented group (race Other on Adult; top-importance identities on IMDb):

| Instance | GAVOT | group-blind | upsample | downsample | LDS | full |
|---|---|---|---|---|---|---|
| Adult prevalence | **.0732** | .1194 | .0746 | .0805 | n/a | .0309 |
| Adult aligned | **.0318** | .0352 | .0325 | .0325 | n/a | .0309 |
| IMDb skewed | **76.99** | 86.42 | 79.95 | 80.23 | 91.04 | 72.23 |
| IMDb aligned | **73.63** | 79.89 | 75.59 | 75.59 | 84.81 | 72.23 |

Reading: self-normalized upsampling is a strong baseline, far ahead of group-blind averaging and
within 0.002 CE / 0.7 MSE of transport on the overall objective. Transport is ahead on every
instance, and by more on the rare group (3 MSE on IMDb skewed, 2 on IMDb aligned). The two are
the same idea at different precision: upsampling is the one-shot heuristic (ratio weights,
normalized per batch), transport is the exact solution of the same marginal problem, with the
feasibility certificate and the floor decomposition attached. Downsampling is never better than
upsampling. On the aligned instances all convex rules tie, as Prop. 2 predicts.

LDS is the wrong axis for this problem and the numbers say so: it is worse than group-blind
averaging on both IMDb instances (94.3 vs 91.6 skewed, 89.4 vs 86.4 aligned) and on the rare
group (91.0 vs 86.4, 84.8 vs 79.9). LDS reweights by how rare a *label value* (an age) is in the
pooled data; the mismatch here is in how rarely a *group* is observed relative to its target
share, which LDS never looks at. Its group weights correlate with the tail tiers, so it behaves
like a mild version of group-blind averaging (tier 5: 95.0, vs 96.6 group-blind, 115.3 GAVOT,
116.7 full). Report it as the imbalanced-regression baseline Herlock asked for, with that one
sentence of explanation; do not tune it (kernel/sigma) into something it is not.

Per-group detail (all groups, most-biased single group): see the 9/20 message to Vihaan; the
rows where group-blind beats every other rule (White on Adult, tier 5 on IMDb) are the groups the
target down-weights, and full coverage is worst there too, so that is the objective at work, not a
failure. Upsampling beating full coverage on tier 2 / tier 5 is the same effect: full minimizes
the p-weighted objective and is best on every group with large p_i; no rule beats full on the
overall objective or on the least represented group.

Where this goes: two more columns in Table 1 (or a small table in the extended version) and one
sentence in E1: "self-normalized upsampling recovers most of the gain and transport the rest;
the un-normalized version is the fixed multiplier, which diverges."

## Winner table (overall objective; Welch t, population std, 5 seeds; |t| >= 2.8 called significant)

| Instance | nu | GAVOT | group-blind | upsample | downsample | LDS | full | winner (excl. full) | runner-up | t | significant? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Adult infeasible | .60 | **0.2269** | 0.2479 | 0.2288 | 0.2308 | n/a | 0.2073 | GAVOT | upsample | 5.75 | yes |
| Adult feasible | 0 | 0.2075 | 0.2077 | 0.2075 | 0.2075 | n/a | 0.2073 | GAVOT | downsample / upsample | 0.44 | no (all convex rules tie, Prop. 2) |
| IMDb infeasible | .31 | **86.06** | 91.63 | 86.74 | 86.90 | 94.28 | 82.95 | GAVOT | upsample | 2.55 | borderline, not at our threshold |
| IMDb feasible | 0 | 84.28 | 86.37 | 84.40 | 84.40 | 89.43 | 82.95 | GAVOT | upsample / downsample | 0.92 | no |

GAVOT vs group-blind is significant in every cell (t 40 / 6.3 / 19 / 11 with the same convention,
from VERIFICATION_2026-09-17.md); the closeness above is GAVOT vs upsampling only.

## Groups where full coverage is NOT the best rule

| Instance | group | target share | GAVOT | group-blind | upsample | downsample | LDS | full |
|---|---|---|---|---|---|---|---|---|
| Adult infeasible | White (majority, 85% of data) | 1/5 | .339 | **.332** | .337 | .337 | n/a | .379 |
| IMDb infeasible | tier 2 | mid | 97.3 | 97.3 | 93.9 | **93.7** | 98.0 | 97.2 |
| IMDb infeasible | tier 5 (least important) | smallest | 115.3 | 96.6 | 111.6 | 111.6 | **95.0** | 116.7 |
| IMDb feasible | tier 2 | mid | 98.5 | **93.7** | 95.2 | 95.2 | 95.1 | 97.2 |
| IMDb feasible | tier 5 | smallest | 117.8 | **107.7** | 114.7 | 114.7 | 108.4 | 116.7 |

Why: full coverage is the exact minimizer of the p-weighted objective, so it spends model capacity
where p is large and gives it up where p is small. The groups above are exactly the low-p ones
(White holds 85% of the data but only 1/5 of the target; tier 5 is the bottom importance
quintile), so the target itself asks for them to be traded away. Rules that under-correct toward
the observed distribution (group-blind, LDS, and to a lesser degree upsampling) spread effort more
evenly and therefore look better on precisely these groups, and worse on the objective and on
the least represented group. GAVOT sits closest to full on every row, which is the intended
behaviour: it optimizes the stated objective, not each group in isolation.

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
