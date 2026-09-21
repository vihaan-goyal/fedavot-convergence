# Cut ledger: main_full (7 pages) -> main_fit (4-page target), 2026-09-19

Rule: nothing is lost for size. Every item that left the 4-page text is listed here with where
it now lives. Three tiers: **main** = `main_fit.tex` (short sections), **appendix** =
`appendix.tex` (one page, included at the end of main_fit), **extended** = `main_full.tex`
(unchanged, the complete paper; the fit version cites it as "the extended version").
Numbers: none changed; `review/VERIFICATION_2026-09-17.md` still applies to both versions.

## Section 5 (experiments_full.tex -> experiments_short.tex)

| Item in the full version | In main_fit | Where the rest lives |
|---|---|---|
| Instances paragraph (20 lines) | 9-line version inside "Instances and protocol": datasets, model, group construction, target, beta families with endpoint nu | appendix E: d = 109 with intercept, 30 images, race split by name, the five groups holding 60% against r ~ K/m, nine/41 infeasible groups at the IMDb endpoints |
| Protocol paragraph (20 lines) | 6 lines: K = 3, H = 5 with the one-step disclosure, the four rules, decay, 4000 steps, 5 seeds, tail-500, floors exact | appendix E: sampler without replacement ~ r, q from 1e6 draws, plan fitted once by eq:ipfp, IPFP row error < 3e-8 at nu = 0 certifying eq:hall, fixed-multiplier definition, full = Phi(p), Newton for logistic |
| Table 1 | unchanged | |
| Fig. 2 | unchanged (figure height 3.0 in -> 2.5 in, same data) | |
| Rare-group figure, two stacked rows (const + decay) | one row, the two decay panels (`figs/rare_group_fit.pdf`) | extended: both rows (`figs/rare_group_adult.pdf`, `figs/rare_group_imdb.pdf`); caption in main_fit says so |
| "The least represented group" (18 lines) | E2, 13 lines; every number kept (.073/.119/.031, .031/.035, 77.0/86.4/72.2, 73.6/79.9, 253/331, 373/380, 219, p/r = 6.7, +-5 to 10) | extended: the sentence on the crossover being "one step earlier still" and "more sensitive of the two" in full |
| "Why transport stops helping" (15 lines) + "E4: the residual is a stepsize artifact." (11 lines) | merged into E4 "why the sign flips", 14 lines; all numbers kept (7.9, 6.99, 6.99 -> 0.02, 105.9, 2.3) | extended: both paragraphs in full |
| "E1: the headline cells." (10 lines) | E1, 8 lines, all numbers kept | extended |
| "E2: the crossover, and where the sign comes from." (13 lines) | renumbered E3, 11 lines, all numbers kept | extended |
| "E3: the $\ell_1$ bound is too loose to be the criterion." (6 lines) | last sentence of E3 | extended: full paragraph |
| "E5: the decomposition in closed form." (17 lines) | one clause in E4 ("both 105.9 at nu = .88, appendix") | appendix B carries every number: .023, 1.58, 82.9/82.95, 105.9, 23.0, 30.7, 454, 105.9 |
| "E6: risk aversion, and where it does not help." (11 lines) + "Why risk aversion does not reach the rare group." (18 lines) | merged into E5, 15 lines; all numbers kept (0.3624/0.3679/0.3994, per-race list, .207/.073, 77.0 -> 103) | extended: the full reasoning paragraph |
| Table 2 | unchanged; caption shortened by one clause | |

## Section 3 (proposed_solution.tex -> proposed_solution_short.tex)

| Item | In main_fit | Where the rest lives |
|---|---|---|
| Kantorovich indicator-cost sentence | dropped | extended |
| Fig. 1, Theorem 3, Corollary 4, Algorithm 1 | unchanged | |
| Feasibility proof sketch, Corollary proof | pointer "proofs are in the appendix" | appendix A (already there) |
| "Severity" paragraph (8 lines) | one sentence inside Corollary 4 | extended |
| "Computing the plan" (22 lines incl. eq:ipfp display) | 9 lines, cost and column property kept | appendix A: the display eq:ipfp and the entropic-dual convergence sentence |
| Lemma 5 and 6 proofs | statements only | appendix A |
| Theorem 7 + "constant free of coverage" paragraph | theorem with a one-sentence remark | appendix A (proof); extended (paragraph) |
| "Outside the feasible region" (15 lines) | 9 lines | extended |
| Theorem 8 | unchanged | proof in appendix A |
| Closing paragraph (9 lines) | 4 lines | extended |

## Section 2 (problem_formulation.tex -> problem_formulation_short.tex)

| Item | In main_fit | Where the rest lives |
|---|---|---|
| Groups and objectives | display eq:target kept; risk definition inline | extended |
| Assumption 1 | kept (referenced by Prop. 2 and Thm. 7) | |
| "Prevalence versus importance" (17 lines) | 11 lines, all definitions kept | extended |
| Proposition 2 | unchanged | proof in appendix A |
| Closing paragraph + boxed question (15 lines) | 7 lines, question inline | extended |

## Appendix (one page)

A proofs (now also Prop. 2, Lemmas 5 and 6, the Sinkhorn display), B closed form, E instances
and protocol in full, C Adult severity table, D per-race table. Order A, B, E, C, D.

## Not cut

Herlock's Secs. 1, 4, 6, abstract, bibliography: untouched. Suggested trims for him in
`review/HERLOCK_TRIM_SUGGESTIONS.md`.

## Second cut, 2026-09-21 (Herlock: put everything on the Overleaf, so main_fit must be 4 pages)

Added first: the imbalance baselines (upsample, LDS columns in Table 1, downsample/LDS in E1 text,
definitions in appendix E, yang2021dir in the bibliography) and the one-sentence schedule note in
the protocol (nine schedules, winner never changes; full table in review/LR_SCHEDULES_2026-09-20.md
and the extended version's protocol paragraph). That put the fit build ~0.7 page over. Cuts, all
recorded in tools/history/{herlock_trims,fit_squeeze,fit_squeeze2,3,4}.py; no number changed:

| Item | In main_fit now | Where the rest lives |
|---|---|---|
| Abstract (his, 22 lines) | 17 lines: "the gap is a bias" sentence and the "nonsmooth convex regime" clause folded; crossing sentence shortened | original/main.tex, main_full.tex |
| Sec. 1 "Groups as clients" (his) | 12 lines: MOT defined in one clause | original, main_full |
| Sec. 1 Contributions (his) | items 2 and 3 merged, as HERLOCK_TRIM_SUGGESTIONS proposed | original, main_full |
| Sec. 1 Related work (his) | one sentence with semicolons | original, main_full |
| Sec. 4 (his) | "heatmap edges" sentence and the "why the layers compose" sentence folded into one clause each | original, main_full |
| Sec. 6 (his) | decomposition sentence (repeats the abstract) removed; last two sentences joined | original, main_full |
| Sec. 2 assumption remark | inside the assumption in parentheses | extended |
| Sec. 2 "known or estimated offline by simulating the sampler"; the FL correspondence sentence | dropped (appendix E has the estimation; Sec. 1 has the correspondence) | appendix E, Sec. 1 |
| Sec. 2 closing paragraph | "The choice of p is thus decorative" version, 7 lines | extended |
| Sec. 3 "any coupling respecting eq:mot serves" | dropped | extended |
| Fig. 1 caption and node spacing | 5 lines, tighter nodes, same figure | extended |
| Sec. 3 "Computing the plan" | 8 lines: |E| <= NM and the "rescaling rows to p and columns to q in turn" gloss dropped (appendix A has eq:ipfp) | appendix A, extended |
| Cor. 4 last sentence ("feasible and infeasible regimes are its two ends") | dropped | extended |
| Sec. 3 Analysis lead-in ("g_i the stochastic subgradient of f_i from B^t cap group i") | dropped (defined in Algorithm 1) | Algorithm 1 |
| Thm. 7 closing clause ("though the realized variance is larger") | dropped | extended, and E4 says it |
| Sec. 3 "Outside the feasible region" | 7 lines | extended |
| Sec. 3 closing sentence "the l1 bound is too loose to discriminate" | dropped here, said in E3 | E3 |
| Algorithm 1 Require line | symbols only | extended |
| Protocol | 21 lines; "the standard practical deviation from the one-step analysis" and the exactness parenthetical dropped (appendix E) | appendix E |
| Table 1 caption; Fig. 2 caption; rare caption; Table 2 caption | shortened, same content; "constant-stepsize panels in the extended version" now only in the ledger | extended |
| E1 | "naive rescaling is no alternative" clause dropped; baseline sentence compressed (numbers 0.2288, 86.74, 84.40, 94.28, 89.43 are in Table 1) | extended |
| E2 | "under both stepsizes", p/r = 6.7, the 373/380 pair at nu = .59, the closing "more sensitively" sentence dropped | extended (all four) |
| E3 | opener folded; l1 sentence reworded | extended |
| E4 | "so the plan delivers at most r_i of its mass", "largest on the rare group", and the closing "Transport helps exactly while there is mass left to move" dropped | extended |
| E5 | per-race list replaced by a pointer to appendix D; "kappa(1,gamma)=1 made visible" and "Risk aversion changes the functional, not who is observed" dropped | appendix D (numbers), extended (sentences) |
| Appendix E | the nine/41 infeasible count and the fixed-multiplier definition dropped (both in Sec. 5 / Table 2) | Sec. 5 |
| Appendix D closing sentence | shortened | extended |
| Figure widths | Fig. 2 0.92 -> 0.82 col, rare 0.99 -> 0.86 col; -6/-8 pt below floats; -4 pt before Sec. 6 | |
| Bibliography | itemsep -2pt so the references stay on page 5 alone | |

Result: main_fit.pdf = 4 pages + references on page 5 + appendix on page 6.

## Section 1 rewrite, 2026-09-21 (Herlock's Overleaf outline)

On the Overleaf Herlock had deleted his Introduction and left four outline lines (what imbalanced
regression/classification is; what SGD does to critical groups, with a simple calculation; the usual
up/down-sampling remedy; a survey of other algorithms) and added Amtej and Vihaan to the author line.
main_fit.tex Sec. 1 now follows that outline (tools/history/intro_outline.py): 'Imbalanced learning',
'What SGD does to a critical group' (one displayed line, eq:introbias, the i.i.d. case of Prop. 2),
'The usual remedies' (sampler tilt bounded by coverage, reweighting = one-shot upsampling, fixed multiplier,
LDS), 'Other algorithms' (reductions, DRO, importance sampling, FedAvg surrogate, FedAVOT/MOT, the
minibatch-as-participation reading), then the Contributions list unchanged. His previous Sec. 1 prose is
intact in original/main.tex and main_full.tex. Author line: his, with 'dfionysis' corrected to 'dionysis'.
Uploaded to the Overleaf (project 6aa9d0263883a32613530d29) 2026-09-21: main.tex (flattened main_fit),
figs/severity_imdb.pdf, figs/rare_group_fit.pdf; compiles there with 0 errors.
