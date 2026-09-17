# Section 3 (Alignment by Masked Optimal Transport) of Herlock's draft: correctness check

Compared against: FedAVOT Thm. 1 (feasibility), Alg. 1 (Sinkhorn), Alg. 2, Lemma 1, Thm. 3;
CAMSAP Sec. 3; previous Overleaf complete.tex Sec. 3 and 3.3; our code
(scripts/pipeline/run_experiments.py) and floors (scripts/pipeline/alignment_diagnostic.py).

Legend: OK = correct; FIX = wrong; ADD = missing; CHECK = theory point for Herlock; NOTE = wording.

| # | His text | Check | Verdict |
|---|---|---|---|
| A1 | MOT constraints (eq. mot) with mask E | identical to FedAVOT (C1-C4)/(MOT) | OK |
| A2 | Fig. 1 example: group 4 only in A_4, so p_4 <= q_4 | singleton Hall: N({4}) = {4}, so p_4 <= q_4 | OK |
| A3 | Thm. 4 (feasibility) | verbatim FedAVOT Thm. 1 | OK |
| A4 | Cor. 5: P[A^t = {i}] <= p_i <= r_i | lower bound from S({i}) = {{i}}, upper from N({i}); correct. Under K-of-N with K >= 2 the lower bound is vacuous (singleton patterns have probability 0) | OK |
| A5 | Cor. 5: iid batch of b examples: b >= log(1-p_i)/log(1-pi_i) | r_i = 1-(1-pi_i)^b >= p_i iff b >= log(1-p_i)/log(1-pi_i) (both logs negative) | OK |
| A6 | Cor. 5: K-of-N uniform: p_i <= K/N | r_i = K/N | OK |
| A7 | nu = 0 iff the upper coverage constraints hold | by definition | OK |
| A8 | "Computing the plan": Sinkhorn once, offline, O(abs(E)), M = realized compositions | our pipeline enumerates all C(100,3) = 161,700 patterns and caches T per instance; abs(E) = 3M. Consistent | OK |
| A9 | "every column Y[.,j] is a probability vector on A_j" | Y = T diag(q)^-1 with column sums q | OK |
| A10 | Alg. 1 lines 6 and 8 (CVaR weights and threshold update) | line 6 = Rockafellar-Uryasev subgradient in theta with p_i replaced by Y[i,j]; line 8 = subgradient in t. Matches our engine's hinge multiplier gamma + (1-gamma)/alpha * 1{f_i > t}. One difference: the code updates t with a SEPARATE step size eta_t (0.05 IMDb, 0.005 Adult); Alg. 1 uses the same eta | ADD (one clause in Sec. 5 if E5 stays) |
| A11 | Alg. 1 vs what was run: line 5 takes one stochastic subgradient per observed group, then the weighted step | the code runs H=5 local full-batch GD steps per observed group and then takes the weighted PARAMETER average (the FedAVOT relay), identically for every rule. The previous Overleaf disclosed this as the standard practical deviation from the one-step analysis | ADD: one sentence, after Alg. 1 or in Sec. 5 Instances |
| A12 | Lemma 6 (unbiasedness) and proof | FedAVOT Lemma 1 logic moved to gradients; row-marginal step correct | OK |
| A13 | Lemma 7 (second moment <= G^2, no dependence on abs(A^t) or N) | Jensen over the probability vector Y[.,j], then sum_i (sum_j T[i,j]) G^2 = G^2. Correct. Proof wording "apply Lemma 6 to norm(g_i)^2" is loose: what is used is the row-marginal identity, not the lemma | NOTE |
| A14 | Thm. 8: rate DG/sqrt(T) with eta = D/(G sqrt(T)) | standard projected subgradient bound with an unbiased oracle of second moment G^2 | OK |
| A15 | "Outside the feasible region": Sinkhorn converges to the I-projection, "the coupling whose reachable row marginal p-hat minimizes KL(. given p)" | The DIRECTION of the KL is not established by the cited results as stated. Csiszar 1975 covers feasible I-projections; for infeasible marginals the IPFP subsequences converge and the limiting row marginal is characterised in Gietl and Reffel 2013, "Accumulation points of the iterative proportional fitting procedure" (Statistics 47(6)). The previous Overleaf and the FedAVOT paper both wrote "closest feasible marginals in the KL sense" without fixing the argument order. Empirically our p-hat is min(p, r) renormalised | CHECK: cite Gietl and Reffel and keep the direction, or write "the KL-closest reachable marginal" without the order |
| A16 | Thm. 10: E[F_p(theta-bar_T)] - F_p(theta*) = [Phi(p-hat) - Phi(p)] + eps_T(p-hat), with eps_T <= DG/sqrt(T); proof: "Theorem 8 applied to F_p-hat bounds the optimization term" | The identity is fine as a DEFINITION of eps_T. The bound is not: Thm. 8 on F_p-hat controls E F_p-hat(theta-bar_T) - F_p-hat(theta-dagger), not E F_p(theta-bar_T) - F_p(theta-dagger). The difference is (F_p - F_p-hat)(theta-bar_T) - (F_p - F_p-hat)(theta-dagger), which is at most 2M * l1(p - p-hat) in general and vanishes only as theta-bar_T approaches theta-dagger (e.g. under strong convexity, which our two instances satisfy). As written, "eps_T <= DG/sqrt(T)" is not proved | CHECK: (a) state the DG/sqrt(T) bound for the p-hat objective and keep the F_p decomposition exact by definition; or (b) add a strong-convexity clause converting the F_p-hat gap into a distance; or (c) write eps_T <= DG/sqrt(T) + o(1). Our measured residuals (1.4 to 2.3 MSE on IMDb) are consistent with any of these |
| A17 | "Both terms available before training: p-hat and p~ from (p, r, E)" | p-hat needs the pattern law q (the Sinkhorn input), not only the rates r; p~ needs q as well (sum over A). Should be (p, q, E) | FIX |
| A18 | "on instances with a closed-form frontier, Phi exactly" | IMDb: closed-form least squares; Adult: Newton on a convex objective to 1e-9, exact for practical purposes | OK |
| A19 | "The l1 bound is the weaker object ... too loose to discriminate" | consistent with our four-cell check (the l1 criterion predicts "helps" in all four cells) | OK |
| A20 | Contributions 3 and abstract: "an alignment gain fixed by the instance and an optimization residual paid by the estimator" | consistent with Thm. 10 once A16 is settled | OK |

## Proposed edits
1. A17: (p, r, E) -> (p, q, E). 0 lines. (FIX)
2. A11: one sentence after Alg. 1 or in Sec. 5: "In the experiments each observed group takes H=5 local steps before the weighted average, the standard practical deviation from the one-step analysis, applied identically to every rule." +2 lines. (ADD)
3. A16: Herlock's call. A minimal safe rewording: replace "<= DG/sqrt(T)" under the brace by "optimization residual", and add after the theorem: "Theorem 8 applied to F_p-hat bounds E F_p-hat(theta-bar_T) - F_p-hat(theta-dagger) by DG/sqrt(T); eps_T additionally carries the p-versus-p-hat mismatch along the trajectory, which vanishes as theta-bar_T approaches theta-dagger." +2 lines. (CHECK)
4. A15: cite Gietl and Reffel 2013 for the infeasible IPFP limit, or drop the KL argument order. 0 to +1 line. (CHECK)
5. A13: proof wording. 0 lines. (NOTE)
6. A10: if E5 stays, state the threshold step size in Sec. 5 (eta_t = 0.05 on IMDb, 0.005 on Adult). +1 line. (ADD)
