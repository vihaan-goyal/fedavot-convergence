# Verification pass, 2026-09-17: numbers, process, and original-vs-ours Section 5

Every number below was recomputed from the raw run summaries
(`results/2026-09-14_severity_sweep/<cell>/summary.csv`, 5 seeds, tail-500), the cached
transport plans (`transport_*.npz`), the floors table
(`figures/2026-09-14_severity_sweep/severity_sweep_table.csv`), the CVaR grid
(`results/2026-09-15_paper_cells/summary.csv`), and the no-training closed-form script
(`scripts/paper_experiments/theory_checks/infeasible_bias_check.py`, re-run today).
Std is population std, Herlock's convention; sample std in brackets where it matters.

## 1. Table 1 (headline cells, decay)

| Instance | GAVOT | group-blind | m/K | full | in text | recomputed t (pop / sample) |
|---|---|---|---|---|---|---|
| Adult prevalence | 0.2269 | 0.2479 | 0.670 (max seed 0.727, none capped) | 0.2073 | same | 44.7 / 40.0 (text: 45) |
| Adult aligned | 0.2075 | 0.2077 | 1e12 cap = div. | 0.2073 | same | 7.1 / 6.3 |
| IMDb skewed | 86.06 | 91.63 | 8504 (spiky, not capped) | 82.95 | same | 20.7 / 18.5 (text: 21) |
| IMDb aligned | 84.28 | 86.37 | 1e12 cap = div. | 82.95 | same | 12.8 / 11.4 (text: 13) |

All match. The "div." entries are exactly the two aligned instances (non-uniform observation
rates), confirming the corrected E1 sentence.

## 2. Table 2 (IMDb sweep, decay), all six rows match to the printed precision

| beta | nu | Delta_floor | gain | t (pop) | residual GAVOT | residual group-blind | const-stepsize gain |
|---|---|---|---|---|---|---|---|
| 0 | .31 | 6.99 | +5.57 | 20.7 | 2.64 | 1.21 | -0.87 |
| 0.5 | .59 | 5.71 | +3.46 | 11.3 | 3.10 | 0.84 | -3.10 |
| 1 | .70 | 3.67 | +2.05 | 5.4 | 2.53 | 0.91 | -3.40 |
| 1.5 | .77 | 2.56 | +0.58 | 1.1 | 2.58 | 0.59 | -5.26 |
| 2 | .82 | 1.62 | -0.03 | -0.1 | 2.40 | 0.75 | -5.52 |
| 3 | .88 | 0.02 | -2.28 | -7.9 | 2.52 | 0.22 | -7.94 |

Derived claims: "excess residual averages 1.9" = 1.87 (ok); "floors 6.99 apart at nu=.31"
(ok); "loses on all six IMDb skews at constant stepsize, by as much as 7.9" (ok: all six
negative, worst -7.94); the sign flips between nu=.77 and .82 where Delta_floor crosses the
residual gap (ok).

## 3. Adult sweep (E2 numbers): gain vs Delta_floor

beta 0: +.0210 vs .0110; 0.25: +.0181 vs .0144; 0.5: +.0134 vs .0129; 0.75: +.0050 vs
.0049; 1: +.0002 vs .0003. All match; t = 44.7 / 69.4 / 35.2 / 35.8 / 7.1 (appendix C ok).

## 4. Per-race (E5 and appendix D), Adult prevalence, decay

White .339/.332/.379, Black .179/.200/.177, Asian-Pac .368/.399/.327, Amer-Ind .175/.189/.123,
Other .073/.119/.031 (GAVOT / group-blind / full). All match. CVaR: worst race GAVOT+CVaR
at (0.2, 0.7) = 0.3624, which is the grid minimum; GAVOT 0.3679; group-blind 0.3994. Match.

## 5. E6 closed form (re-run today, no training)

||p - p_hat||_1 = 1.581 (text 1.58); max |p_hat - min(p, r)| = 0.0234 (text .023);
Phi(p) = 82.94 (text 82.9; measured full 82.95); Phi(p_hat) = 105.88 (text 105.9); floor
gap 22.93 (text 23.0); exact bias |(p - p_hat) . L(theta_dagger)| = 30.65 (text 30.7);
M >= max_i L_i = 454.4 (text 454); Phi(p_tilde) = 105.90 (text 105.9). All match.

## 6. Protocol paragraph claims vs the runner (`scripts/pipeline/run_experiments.py`)

| Claim in text | Source | Verdict |
|---|---|---|
| K = 3, 4000 steps, 5 seeds, tail-500 | `--k`, `--rounds 4000`, `--tail 500` | ok |
| H = 5 local steps per observed group | `--local-epochs` default 5 | ok |
| q from 1e6 sampler draws | `q_samples = 1000000` in every transport npz | ok |
| plan computed once per instance | transport npz cached per cell | ok |
| stepsize eta/(1+t/1000) | `--lr-decay 1000` in the decay cells | ok |
| Adult d = 109 with intercept | loader `X_all.shape = (100, 30, 109)` | ok |
| Adult 100 groups x 30, split 85/10/3/1/1 | loader (`group_names`) | ok |
| five groups of the three smallest races hold 60% | 3 + 1 + 1 groups x 1/5 per race = .60; `n_infeasible = 5`, mass .600 | ok |
| IMDb 128-d ResNet embeddings, first 100 identities with 30 images | `imdb_embeddings.npy`, `groups[:N]` | ok |
| nine infeasible groups at beta = 0, 41 at beta = 3 | `n_infeasible` 9 / 41; masses .313 / .877 | ok |
| nu from 0 to .88 across 11 instances | table | ok |
| IPFP converges "to 1e-8" at nu = 0 | row errors 2.4e-8, 2.9e-8, 5.4e-9 | **too strong; changed to "below 3e-8"** |
| floors exact: closed form LS / Newton logistic | `alignment_diagnostic.cell_floors` | ok |

## 7. Original Section 5 vs ours: what changed and whether it makes sense

Diff: `original/main.tex` lines 489-622 against `sections/experiments_full.tex`.

| Change | Why | Verdict |
|---|---|---|
| Instances paragraph rewritten with models, dimensions, stepsizes, group construction, target formula, the beta families with their nu values | his version said "importance target over age tiers" (wrong: the target is cubic over identities) and gave no model, stepsize, or group construction; a reader could not reproduce the instances | keeps every number he had, adds only facts from the runner; sensible |
| New Protocol paragraph | his draft never says how q is obtained, that the plan is computed once, that every rule takes H = 5 local steps (his Algorithm 1 is one-step; the previous Overleaf disclosed this), how the four rules are defined, or how the floors are computed | needed for honesty about H = 5 and for reproducibility; sensible, but it is 14 lines and is the first thing to cut if space is short |
| Table 1: m/K on Adult prevalence "div." -> 0.670 | measured; no seed capped | correction |
| E1: "diverges on every instance" -> "on both aligned instances, far off on the other two" | matches Table 1 | correction |
| Fig. 2 PNG crop -> regenerated vector PDF, 0.92 column width | his PNG had the title cut mid-line and our internal axis label | cosmetic, same data |
| Table 2 caption: states t is Welch on population std | his t values are population-std; without saying so a reader recomputing with sample std gets 40/19/11 and thinks the table is wrong | sensible |
| E2: added the two Adult skews where gain exceeds Delta_floor (.0210 vs .0110, .0181 vs .0144) | his text reported only the three that match; the two that exceed are also evidence for the decomposition (group-blind sits further above its floor) | makes the claim complete rather than selective |
| E2 / E3 closing sentences shortened | page budget; no content lost | fine |
| New E6 paragraph (closed form on the mirrored instance) | this is the one place the decomposition is checkable exactly; it explains why beta = 3 is the instance where transport loses under decay | sensible; duplicates appendix block B, so one of the two must go |
| E6 wording "the one instance where transport still loses" | beta = 2 is a tie (-0.03, t = -0.1), beta = 3 is the only significant loss | **reworded today to say "by a significant margin" and name the tie** |

Everything else in Section 5 (E1 to E5 text, both tables, the figure caption) is his, verbatim.

## 8. Rare-group figures (`figures/2026-09-17_rare_group/`)

Read directly from `group_tail_Other` / `group_tail_Amer-Indian-Eskimo` / `group_tail_tier1`
in the same summary files; no new computation beyond mean and population std over seeds.
Headline (decay): Adult Other .0732 / .1194 / .0309; Adult aligned .0318 / .0352 / .0309;
IMDb tier 1 76.99 / 86.42 / 72.23; IMDb aligned 73.63 / 79.89 / 72.23. Adult sweep: GAVOT
wins on Other and on Amer-Indian at all five betas, both stepsizes. IMDb tier 1, decay: wins
at beta 0, 0.5, 1 (+0.14, a tie), loses at 1.5, 2, 3; constant: wins only at beta 0. Same
crossover as the overall objective, one step earlier.

## Not verified today

- His t-values 45 / 21 / 13 are rounded population-std values; fine.
- The Adult accuracy metric Herlock also mentioned: not computed anywhere (runner logs
  losses only).
