# Section 5 (Experiments) of Herlock's GAVOT draft: claim-by-claim check

Source of truth: results/2026-09-14_severity_sweep/<cell>/summary.csv (5 seeds, 4000 steps,
tail-500, LR decay eta/(1+t/1000)), figures/2026-09-14_severity_sweep/severity_sweep_table.csv
(closed-form floors), results/2026-09-15_paper_cells/ (CVaR grid). Raw recomputation in
section5_numbers.txt. "t" = Welch t on 5 seeds each; "sample" uses n-1 std, "pop" uses n std.

Legend: OK = matches; FIX = wrong; ADD = true but incomplete; CHOICE = convention, his call.

## Instances paragraph
| # | His text | Ours | Verdict |
|---|---|---|---|
| I1 | IMDb-Wiki "with a skewed importance target over age tiers" | importance is cubic over the 100 celebrity identities, p_i ~ (101-i)^3; "tiers" are only our reporting quintiles | FIX |
| I2 | "m=100 critical groups, K=3, 4000 steps, 5 seeds, tail-500" | same | OK |
| I3 | "eleven instances", nu from 0 to 88% | 6 IMDb (nu .31,.59,.70,.77,.82,.88) + 5 Adult (.60,.60,.40,0,0) | OK |
| I4 | Adult family "from prevalence-proportional to importance-aligned" | beta=0 is uniform r (every group equally observable; groups per race are prevalence-proportional), beta=1 is r ~ p | OK (wording is his) |
| I5 | model, data and step sizes | not stated anywhere: Adult = logistic regression, d=109, 30 samples/group, 85/10/3/1/1 groups per race, eta=0.1; IMDb = linear regression on 128-d ResNet embeddings, 30 images/identity, eta=1e-2 | ADD |
| I6 | local steps | not stated: every observed group takes H=5 local full-batch steps, then the weighted parameter average (FedAVOT relay). Alg. 1 shows one weighted subgradient step. Previous Overleaf disclosed this ("affects all rules identically") | ADD (also flagged in Sec. 3 check) |
| I7 | "floors Phi(p), Phi(p_hat), Phi(p_tilde) are exact" | closed-form LS on IMDb; Newton on the convex logistic objective on Adult (exact to 1e-9) | OK |

## Table 1 (headline cells)
| # | Cell | His | Ours (sample std) | Verdict |
|---|---|---|---|---|
| T1a | Adult prevalence: GAVOT / unif / m/K / full | 0.2269 / 0.2479 / div. / 0.2073 | 0.2269+-0.0006 / 0.2479+-0.0010 / **0.670+-0.035, 0 of 5 seeds capped** / 0.2073 | FIX m/K: not divergent |
| T1b | Adult aligned | 0.2075 / 0.2077 / div. / 0.2073 | 0.2075 / 0.2077 / capped 5/5 / 0.2073 | OK |
| T1c | IMDb skewed (beta=0) | 86.06 / 91.63 / 8504 / 82.95 | 86.06+-0.24 / 91.63+-0.63 / 8504+-1.9e4, 0 capped / 82.95 | OK |
| T1d | IMDb aligned | 84.28 / 86.37 / div. / 82.95 | 84.28+-0.17 / 86.37+-0.38 / capped 5/5 / 82.95 | OK |
| T1e | caption: "m/K diverges whenever observation rates are non-uniform" | diverges on the two aligned (non-uniform r) cells; under uniform r it is finite but bad (0.670 Adult; 8504 IMDb, spiky) | OK as stated; E1 sentence below is not |

## E1
| # | His | Ours | Verdict |
|---|---|---|---|
| E1a | t = 45 (Adult prev.), 21, 13 (IMDb) | sample: 40.0, 18.5, 11.4; pop: 44.7, 20.7, 12.8 | CHOICE: his = population std. Either is fine; state the convention once |
| E1b | "The fixed multiplier diverges on every instance" | diverges on 2 of 4 (aligned); finite on the other 2 | FIX |
| E1c | Adult aligned: GAVOT and unif "coincide at the oracle value" | 0.2075 vs 0.2077 vs full 0.2073 | OK |

## Table 2 (IMDb sweep) and E2
| beta | nu | dfloor (his / ours) | gain (his / ours) | t (his / ours sample / pop) |
|---|---|---|---|---|
| 0 | .31 | 6.99 / 6.99 | +5.57 / +5.57 | 20.7 / 18.5 / 20.7 |
| 0.5 | .59 | 5.71 / 5.71 | +3.46 / +3.46 | 11.3 / 10.1 / 11.3 |
| 1.0 | .70 | 3.67 / 3.67 | +2.05 / +2.05 | 5.4 / 4.9 / 5.4 |
| 1.5 | .77 | 2.56 / 2.56 | +0.58 / +0.58 | 1.1 / 1.0 / 1.1 |
| 2.0 | .82 | 1.62 / 1.62 | -0.03 / -0.03 | -0.1 / -0.1 / -0.1 |
| 3.0 | .88 | 0.02 / 0.02 | -2.28 / -2.28 | -7.9 / -7.1 / -7.9 |
All OK except the t convention (CHOICE, same as E1a).
| # | His | Ours | Verdict |
|---|---|---|---|
| E2a | "excess residual transport pays averages 1.9" | mean(dfloor - gain) over the 6 IMDb skews = 1.87 | OK |
| E2b | sign flips between beta 1.5 (2.56, +0.58) and 2.0 (1.62, -0.03) | same | OK |
| E2c | Adult: gain tracks dfloor "within 4% at three of five (.0134/.0129, .0050/.0049, .0002/.0003)" | true for beta 0.5, 0.75, 1.0 | OK but see E2d |
| E2d | (silent) | at beta 0 and 0.25 the gain EXCEEDS dfloor: .0210 vs .0110, .0181 vs .0144. Reason: group-blind averaging sits further above its own floor there (residual 0.020 vs GAVOT's 0.010). A reader with the CSV will see it | ADD one clause |
| E2e | "five Adult skews all sit above their crossover" | all five gains positive | OK |

## E3
| # | His | Ours | Verdict |
|---|---|---|---|
| E3a | ||p-p_hat||_1 < ||p-p_tilde||_1 in all eleven, incl. the three where transport loses or ties | true in the 4 checked cells (alignment_diagnostic.py); IMDb beta 1.5-3 by monotonicity of the sweep table | OK |

## E4
| # | His | Ours | Verdict |
|---|---|---|---|
| E4a | constant step: transport loses on all six IMDb skews, "by as much as 7.9" | const-LR gains: -0.87, -3.10, -3.40, -5.26, -5.52, -7.94 | OK |
| E4b | "even at nu=.31 where the floors are 6.99 apart" | same | OK |
| E4c | schedule eta_t = eta/(1+t/1000) | same (T0 = 1000) | OK |

## E5 (CVaR)
| # | His | Ours | Verdict |
|---|---|---|---|
| E5a | overall objective minimised on the gamma=1 edge on every instance | best grid point is gamma=1.00 in all 4 cells for both combos (Adult aligned GAVOT+CVaR best at (0.9,0.9) = 0.2075, equal to gamma=1 to 4 decimals) | OK |
| E5b | worst race, Adult prevalence: GAVOT+CVaR (0.2,0.7) 0.3624 vs GAVOT 0.3679 vs group-blind 0.3994 | 0.3624 @ (0.20,0.70); 0.3679; 0.3994 (worst race = Asian-Pac-Islander) | OK |
| E5c | per race: Black .179/.200, Asian-Pac .368/.399, Am-Ind .175/.189, Other .073/.119, White .339/.332 | .1792/.1995, .3679/.3994, .1752/.1888, .0732/.1194, .3391/.3323 | OK |

## Figure 2
| # | His | Ours | Verdict |
|---|---|---|---|
| F1 | figs/severity_imdb.png | a crop of our figures/2026-09-14_severity_sweep/severity_sweep_K3_4000rounds.png: the suptitle is cut mid-line ("(solid = 5-seed mean ±1 std, dashed = ..."), the x-axis uses our pi_i, the legend says "Full participation" and "Uniform average over K" (not his vocabulary), raster | FIX: regenerate as vector in his notation (nu, group-blind average, Phi); same aspect ratio so the page budget holds |
| F2 | caption: left constant / right decaying; "floors seven units apart" | matches the data | OK |

## Summary of proposed changes to Section 5 (for approval)
1. Table 1: Adult prevalence m/K "div." -> 0.670. (FIX, T1a)
2. E1: "diverges on every instance" -> diverges on both aligned instances and is far off on the other two. (FIX, E1b)
3. Instances: "over age tiers" -> over the 100 identities. (FIX, I1)
4. Instances: add model, data, step sizes and the H=5 local-step disclosure; ~4 lines, paid for by trimming E3's last sentence and E2's closing sentence. (ADD, I5, I6)
5. E2: add the clause on the two Adult skews where the gain exceeds the floor gap. (ADD, E2d)
6. Fig. 2: regenerate. (FIX, F1)
7. t statistics: leave his (population std) or switch to sample std; either way, say which in the Table 2 caption. (CHOICE)
Nothing else in Section 5 needs to change.
