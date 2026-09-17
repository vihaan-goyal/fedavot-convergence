# Fresh write-ups of Secs. 2, 3, 5 (Herlock's 9/15 ask), 2026-09-15 late

Herlock: "work excessively on problem definition; proposed approach and experiment section;
look at the previous overleaf we had" / "write up the problem formulation; and Our Proposed
solution section. Look at FedAvot and CAMSAP papers".

Everything is local in `paper/gavot_draft/`. Nothing in `main.tex` (the correctness-pass
version) was changed. Herlock's Overleaf untouched.

## Files

| File | What | Replaces |
|---|---|---|
| `problem_formulation.tex` | Sec. 2, "Problem Formulation" | his Sec. 2 "Group-Blind SGD and its Surrogate" |
| `proposed_solution.tex` | Sec. 3, "Proposed Approach: Alignment by Masked Optimal Transport" | his Sec. 3 |
| `experiments_full.tex` | Sec. 5, his verified text + protocol + closed-form validation | his Sec. 5 |
| `main_full.tex` / `.pdf` | his paper with all three new sections inputted | test build |
| `main_rewrite.tex` / `.pdf` | his paper with only Secs. 2 and 3 replaced | test build |
| `appendix.tex` | block A is now "Proofs" (feasibility sketch, corollary, rate, infeasible) | old block A (rate proof only) |

All labels (`sec:setup`, `prop:surrogate`, `eq:target`, `eq:mot`, `fig:mask`, `thm:feas`,
`cor:batchsize`, `eq:batchlaw`, `alg:gavot`, `lem:unbiased`, `lem:variance`, `thm:rate`,
`thm:infeasible`, `eq:infeasible`, `sec:exp`, tables, figure) are kept, so his Secs. 1, 4, 6
compile against the new sections unchanged. New labels: `ass:std`, `eq:ptilde`, `eq:hall`,
`eq:ipfp`, `eq:rate`. Both test builds compile with zero undefined references.

## What the new sections contain

**Sec. 2 (structure of FedAVOT Sec. 1 + CAMSAP Sec. 2).**
Groups, prevalence, per-group risks, ERM as F_pi, the importance target F_p (eq:target),
Assumption 1 (convex compact C, diameter D, 0 <= f_i <= M, second moment G^2), the batch as
an active set A^t with composition law q, observation rate r_i = sum_{A ∋ i} q(A) with the
i.i.d. formula r_i = 1 - (1 - pi_i)^b, the FL correspondence, the hierarchical experiment of
CAMSAP eq. (4), Proposition (surrogate objective) WITH proof (his had none), the bias
discussion (p~_i <= r_i always, so tilting the sampler cannot reach p_i > r_i; upscaling
destabilizes), and the FedAVOT-style boxed question. His wording was reused wherever it was
already right.

**Sec. 3 (structure of FedAVOT Secs. 2-3).**
Coupling Y/T, MOT (eq:mot) with the Kantorovich indicator-cost remark, his Fig. 1 verbatim,
Theorem (feasibility) with the max-flow sketch, Corollary (coverage law, nu) with proof,
severity paragraph, Sinkhorn as a displayed update (eq:ipfp) with cost and convergence via the
entropic dual, his Algorithm 1 verbatim, Lemma (unbiased) and Lemma (second moment) with
proofs, Theorem (rate) with proof, the "constant free of coverage" paragraph, the infeasible
regime with the reachable polytope R(q,E) and the Gietl-Reffel citation, Theorem (infeasible
regime) restated so that the residual bound is on F_p-hat (the correct statement; see
section3_check.md A16), with proof, closing paragraph. To hold length, the proofs of the
feasibility theorem, the corollary, the rate theorem and the infeasible theorem are in the
appendix ("Proofs are in the appendix." after Thm. feas); the two lemma proofs stay inline.

**Sec. 5.** His text (already verified number by number) plus, from the previous Overleaf:
an Instances paragraph with the full dataset/group construction, a Protocol paragraph
(sampler, q from 1e6 draws, H=5 local steps applied to all rules, the four rules defined,
tail-500, how the floors are computed, IPFP convergence certificate at nu = 0), and a new
paragraph E6 (the decomposition read off in closed form on the mirrored instance:
p-hat ~ min(p, r), l1 gap 1.58, Phi(p) = 82.9 vs measured 82.95, Phi(p-hat) = 105.9, exact
bias 30.7, M >= 454, uniform floor also 105.9 so Delta_floor = 0). E6 duplicates appendix
block B; if E6 stays in the main text, drop block B.

## Page budget (the problem)

| Build | Pages | Content ends |
|---|---|---|
| `main.pdf` (his draft + correctness pass) | 5 | page 4 full, references page 5 |
| `main_rewrite.pdf` (new Secs. 2, 3) | 6 | page 5 about 65% full |
| `main_full.pdf` (new Secs. 2, 3, 5) | 6 | page 5 about 90% full |

So the fresh write-ups are about one column over (Secs. 2+3) to one page over (all three)
the 4-page limit, after already moving four proofs to the appendix and trimming prose. This
is the trade-off Herlock has to call: he asked for both "excessive" work on these sections
and 4 pages + 1 appendix page. Candidate cuts, largest first, none of which touch numbers:
1. Sec. 2: drop the proof of the proposition (6 lines) and Assumption 1 as an environment
   (fold into one sentence, 4 lines).
2. Sec. 3: drop the Sinkhorn display eq:ipfp and its convergence sentence (7 lines); drop
   the "constant free of coverage" paragraph (6 lines); drop the Kantorovich sentence (2).
3. Sec. 5: drop the Protocol paragraph back to his one-liner (14 lines); drop E6 and keep
   appendix B (16 lines).
4. His own sections: the Contributions list (Sec. 1) and Related work are 30 lines; Sec. 4
   (CVaR) is 55 lines and E5 depends on it.
Items 1-3 together recover roughly one page and give back most of what was added; the honest
version of "fits in 4 pages" is close to the correctness-pass `main.tex` plus the appendix.

## Appendix

`appendix_standalone.pdf` (page 2 is the appendix; page 1 is stub labels) still fits on one
page with the four proofs, block B, the Adult severity table and the per-race table. The [?]
citations in the standalone preview are only because the wrapper has no bibliography; they
resolve when pasted into main.tex.

## Not done / for Herlock

- The synthetic feasibility-boundary study and the mechanism figure from the previous
  Overleaf (constant stepsize, old vocabulary) are not carried over; they would need a rerun
  under decay to be consistent with Table 2.
- His FILLIN (exact-penalty arXiv number) is still there.
- Which of the three builds to push is his decision; my recommendation is `main_full` as the
  version he presents to Dionysis (it reads as a complete paper) and the cut list above for
  the submission.
