# Review of complete.tex (OT-SGD paper, Herlock's Overleaf)

Reviewed 2026-07-15, per Herlock's 7/15 request: "read the complete.tex files very
carefully and see if it is clear and the narrative is convincing?"

Source: Overleaf project "OT-SGD: Optimal Transport Aware Stochastic Gradient Descent
to Mitigate Distribution Shift", cloned at `C:\Users\goyski\fedavot-overleaf`
(git pull there to refresh). `complete.tex` is the live file; `main.tex` is an older
draft with the intact heading structure. Compiles clean (tectonic), 9 pages.
All experimental numbers in Section 4 verified against our repo runs: correct.

## Overall verdict

The story makes sense and the experiments support it well: "group reweighting is easy
when any batch can contain any group; when batches only reveal subsets, it becomes a
transport feasibility problem, and feasibility (not the aggregation rule) decides
whether the target objective is reachable." Three real problems remain, and a reviewer
would catch all of them.

## Problem 1: A promised experiment isn't there (BIGGEST)

- [x] Experiment rebuilt (2026-07-15): `scripts/adult_fairness.py` →
  `figures/adult_race_K3_2000rounds.*` + `data/adult_race_K3_2000rounds_curves.npz`.
  Amtej's original pipeline was never committed (only PNGs); this is a NEW design that
  fits the paper's feasibility narrative: group-homogeneous clients (race, users per
  group ∝ prevalence: 85/10/3/1/1), group-uniform importance p (1/5 per race = the
  fairness target), two availability regimes. PREVALENCE (uniform clients, the realistic
  default): 5/100 users infeasible holding 60.0% of importance mass, IPFP stalls at
  1.7e-1 → FedAVOT 0.2278 ± 0.0018 vs FedAvg(K) 0.6720 ± 0.0886 vs full 0.2068 (tail-500,
  5 seeds; FedAVOT within 10% of full, FedAvg(K) 3.3x worse). ALIGNED (r ∝ p): feasible,
  IPFP 2.9e-8 → FedAVOT 0.2076 ± 0.0001 ≈ full 0.2068; FedAvg(K) DIVERGES (same
  mechanism as IMDb-Wiki). Headline: "equal client availability does not make a
  group-uniform fairness target reachable"; the residual loss lands exactly on the
  minority groups the target was meant to protect (Amer-Indian 0.175 vs full's 0.122,
  Other 0.072 vs 0.030).
- [x] Setup/results paragraphs written and PUSHED to the Overleaf 7/15 (commit 1738c26),
  after Herlock's "Can you edit it!? I will give it a full read afterward": old Adult
  paragraph replaced with the new design, results paragraph + figure* block added,
  `adult_race_K3_2000rounds.pdf` uploaded, protocol paragraph generalized ("two
  experiments" -> all, squared-loss line now names CE for Adult). Herlock still owes
  the full read.

The abstract and intro both say the method is tested on two datasets: Adult
(income/fairness) and IMDb-Wiki. Section 4 describes the Adult dataset in a full
paragraph. Then there are no Adult results at all: no figure, no numbers.
The intro's headline claim ("Across both, FedAVOT tracks the full-participation
objective whenever the transport problem is feasible") is only ever supported for
IMDb-Wiki and the synthetic study.

Fix: either add Amtej's Adult results (Oct 2025) or delete every mention of Adult
(abstract, intro, and the Section 4 paragraph). Herlock's call.

## Problem 2: Theory and experiments don't connect on the infeasible case

- [x] Add a bridging paragraph + compute ||p - p_hat||_1 from data we already have
  — DONE 7/15: `scripts/infeasible_bias_check.py` computes everything; bridging
  paragraph "Empirical Validation of the Infeasibility Bound" (incl. the lambda-sweep
  sentences) added at the end of Section 4 and PUSHED to the Overleaf 7/15
  (commit 1738c26, together with the Problem 1 Adult content).

Computed numbers (saved to `data/imdbwiki_infeasible_bias_check.npz`):

- Mirrored IMDb-Wiki regime: ||p - p_hat||_1 = 1.58 (max possible is 2); the stalled
  IPFP marginal is essentially the ceiling truncation, p_hat ~= min(p_i, pi_i)
  renormalized (max deviation 0.023).
- Task is linear regression, so both minimizers are exact in closed form:
  F_p(theta_p*) = 82.9 (matches the measured full-participation plateau 83.07,
  validating the setup); F_p(theta_phat*) = 105.9. The marginal shift alone costs
  22.9 of the measured 33.3 gap (116.40 - 83.07); the remaining ~10 is optimization
  error (K=3 sampling variance, H=5 local epochs, fixed LR), consistent with finding 5.
- Exact bias at the surrogate optimum |(p - p_hat) . L(theta_phat*)| = 30.7. The
  worst-case bound 2B||p - p_hat||_1 holds but is loose (~44x): B >= max_i L_i ~ 454.
- Synthetic sweep: ||p - p_hat||_1 = 0.08 / 0.49 / 0.87 / 1.18 / 1.57 for
  alpha = 0.5/1/1.5/2/3, tracking the 1.01x -> 8.4x degradation. Note alpha=0.5 has
  ~14% infeasible mass yet ratio 1.01: the loss impact tracks ||p - p_hat||_1, not
  the violator count — a good argument for reporting this quantity.

- [x] Run the REGULARIZED variant (Sidak's push, 7/15): `scripts/regularized_transport_sweep.py`
  → `figures/imdbwiki_regularized_K3_4000rounds.*` + npz. Sec 3.3's lambda-penalized
  problem (eq. general-reg-failure) with KL marginal penalty, C=0 on the mask, eps=1,
  solved by unbalanced Sinkhorn: row update u = (p/(Mv))^kappa, kappa = lambda/(lambda+1),
  columns hard. kappa=1 IS the plain masked IPFP of all other experiments; kappa=0 IS
  uniform averaging over the drawn subset. Swept kappa = 0/0.2/0.5/0.8/0.95/1 on the
  mirrored IMDb-Wiki regime, 4000 rounds, 3 seeds:

  | kappa | lambda | \|\|p-p_hat\|\|_1 | predicted floor | measured |
  |---|---|---|---|---|
  | 0 (uniform) | 0 | 1.742 | 105.91 | 108.51 ± 0.77 |
  | 0.2 | 0.25 | 1.644 | 104.00 | 108.33 ± 0.84 |
  | 0.5 | 1 | 1.588 | 104.77 | 112.11 ± 0.78 |
  | 0.8 | 4 | 1.581 | 105.63 | 115.19 ± 0.67 |
  | 0.95 | 19 | 1.581 | 105.84 | 116.30 ± 0.71 |
  | 1 (plain IPFP) | inf | 1.581 | 105.88 | 116.47 ± 0.67 |

  (full participation: measured 83.07, closed form 82.94.)

  THE FINDING: in this regime lambda tunes the VARIANCE, not the bias. The reachable
  polytope is so far from p that every KL projection lands near the ceiling truncation:
  ||p - p_hat||_1 only moves 1.74 -> 1.58 and the closed-form floor is flat (104-106,
  even non-monotone: lowest at lambda=0.25). But the measured loss RISES 108.3 -> 116.5
  with lambda, i.e., the overhead above the floor grows 2.6 -> 10.6 MSE: stronger
  marginal penalties make the per-round weights more extreme without buying reachability.
  This QUANTITATIVELY RESOLVES the CVaR study's open question (uniform averaging = the
  kappa=0 endpoint, measured 108.5 in both studies): uniform wins under infeasibility
  because its floor is essentially the same (105.91 vs 105.88) and its weights have
  minimal variance. Caveat for the paper: Sec 3.3 currently SELLS lambda as a bias knob
  ("larger lambda encourages tighter adherence to p"); in the strongly-infeasible regime
  that adherence is impossible and the knob mostly buys variance — the honest framing is
  a bias-variance tradeoff where SMALL lambda is preferable once infeasibility is severe.
  (Implementation footgun, documented in the script: the damped form Y *= (p/rowsum)^kappa
  is NOT the penalized problem — its fixed point is kappa-independent; and the u-v scaling
  form overflows at kappa=1 where the hard-constraint scalings diverge, so the kappa=1
  endpoint must run the dense bounded-Y IPFP.)

What the theory says (Sec 3.3): when transport is infeasible, run the
entropy-regularized projection; it returns the closest reachable target p_hat, and the
suboptimality bound is O(1/sqrt(T)) + 2B*||p - p_hat||_1.

What our experiments do: run plain UNREGULARIZED masked IPFP, watch the row error
stall at ~4e-2, and interpret the loss plateau as an irreducible floor. The key link
(now stated in the new paragraph): IPFP's final scaling step matches the column
marginal q exactly, so the expected per-round aggregation weight of user i is exactly
p_hat_i = (T 1)_i — training literally minimizes F_{p_hat}, eq. (phat-failure)'s
surrogate, making the bias term of eq. (infeasible-rate) directly measurable.

(Technical nit for Herlock, same area: as written, the entropic projection in eq.
(entropic-mot-failure) has NO dependence on p (constant cost on the mask, only column
constraints), so "closest to p" only follows for the lambda-penalized version given
later. Also the constant B in the bias bound is never defined.)

## Problem 3: The obvious rival baseline is never addressed (Horvitz-Thompson)

- [ ] Add one related-work paragraph naming the HT tradeoff

The most likely reviewer question: "Why optimal transport at all? Weight each
participating client by p_i / pi_i (importance over inclusion probability). Textbook,
and unbiased even in the infeasible case."

The paper has a great answer it never states: HT weights exceed 1 exactly when the
problem matters (p_i > pi_i), so variance explodes and iterates can diverge, which is
precisely what FedAvg(K)'s fixed N/K correction does in our aligned-regime experiment.
FedAVOT's transport weights are convex per column (never exceed 1), so it stays stable
and pays a bounded, quantified bias instead. Stability vs bias is the real tradeoff.
The related-work line about "fixed, known correction factors" gestures at this but
never names it.

## Smaller credibility points

- [ ] 4. Theorem 1 ownership: the abstract claims the feasibility condition as a
  contribution ("we give a max-flow/min-cut style condition"), but the theorem is
  cited to Villani / Peyre-Cuturi as known. Hall (1935) and Ford-Fulkerson are in the
  bib and never cited, and this result descends from them. Pick one: adaptation
  (cite properly, soften the claim) or contribution (prove it).
- [ ] 5. Local epochs: the analysis covers single weighted gradient steps; experiments
  do H=5 local epochs then parameter averaging. Standard FL slack; needs one sentence.
  Similarly the theory treats q as given while experiments estimate it from 1e6 MC
  draws; half a sentence in Sec 2.
- [ ] 6. Feasibility condition cross-ref: the experiments protocol states "feasible
  precisely when p_i <= pi_i". Should cite Theorem 1 and say the general condition
  "reduces to" this in our setting (singleton case).

## Clarity issues

- [ ] Section 2 is a 3-page wall of prose: the \subsection and \paragraph structure
  was stripped when main.tex was flattened into complete.tex, leaving ~15 bare
  "{Heading.}" braces that render as plain inline text. Restore as \paragraph{...}.
- [ ] Section 3.3 states its one idea (p_hat is the closest feasible target, bias is
  controllable) four times: Interpretation / Geometric interpretation / Practical
  implications / Summary. Could lose a third of its length.
- [ ] Notation collision: N = number of samples in eq. (1), N = number of groups in
  Theorem 1, N = number of users in Sec 4. Also mu vs p declared equal then mixed.
- [ ] The worked example after the IPFP algorithm assigns batch weights from T where
  the algorithm uses the normalized Y. Same T-vs-Y trap as our code (see CLAUDE.md
  notation warning); genuinely confusing at the paper's most important distinction.

## Mechanical fixes (can do ourselves in the clone, then push with Vihaan's OK)

- [ ] Title is truncated: ends with a colon + \vspace{-8pt}. Intended subtitle is
  probably the Overleaf project name ("...to Mitigate Distribution Shift").
- [ ] Leftover IEEEtran boilerplate: \markboth line ("Shell et al.: Bare Demo...").
- [ ] Duplicate references: Villani book cited as villani2008optimal AND
  villani2009optimal; Benamou et al. as benamou2015iterative AND benamou2015Iterative;
  Liero et al. as liero2018optimal AND liero2018hk. Each appears twice in the
  reference list. Bib also has literal same-key duplicates (villani2003topics,
  li2020federated).
- [ ] FedAVOT acronym is never expanded anywhere.
- [ ] Mangled sentence in results prose: "...improves over partial-participation
  FedAvg. Final importance-weighted MSE 116.40..." (period should be a colon).
- [ ] 78% vs 87% at alpha=3: mechanism caption says 78% of importance mass
  undeliverable, sweep prose says ~87% infeasible mass. Both correct (undeliverable
  excess sum(p_i - pi_i) vs total mass held by violating users) but reads as a
  discrepancy; add one distinguishing clause.

## Status notes

- Author list: DONE by Vihaan 7/15 (edited spconf.sty line 174 default, matching
  Herlock's own pattern: "Herlock Rahimi, Amtej Sodhi, Vihaan Goyal"). Still missing:
  Herlock's friend (name unknown) and Dionysis Kalogerias; those are Herlock's to add.
- Venue question: 9 pages, journal-style boilerplate. This is NOT the accepted ICASSP
  FedAVOT paper (arXiv:2509.14444); it is a new, longer, generalized paper. Ask
  Herlock what venue it targets; that decides how much trimming matters.
- CVaR / uniform-averaging study (concluded 7/11) appears nowhere in the paper;
  decision still open.
