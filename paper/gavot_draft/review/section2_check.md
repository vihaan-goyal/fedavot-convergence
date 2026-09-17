# Section 2 (Group-Blind SGD and its Surrogate) of Herlock's draft: correctness check

Compared against: FedAVOT (arXiv 2509.14444) Sec. 1 (objective (1), availability q over subsets
A_j, surrogate (2)); CAMSAP 2025 Sec. 2 (marginal p_i = sum_j q(A_j) 1[i in A_j]/|A_j|, eqs. (2)
and (4), Lemma 1); previous Overleaf complete.tex Sec. 2.

Legend: OK = correct; FIX = wrong; ADD = missing; NOTE = worth a look, his call.

| # | His text | Check | Verdict |
|---|---|---|---|
| S1 | Setup: N groups, prevalences pi, risks f_i, C convex compact, F_p, theta*; ell convex bounded by M, subgradient second moment G^2, diameter D | matches FedAVOT Sec. 1 / Assumptions 1-2 and CAMSAP Assumptions 1,3, restated for groups | OK |
| S2 | "Uniform p is the category-uniform objective, p_i ~ 1/pi_i the inverse-prevalence one" | fine (p ~ 1/pi normalised) | OK |
| S3 | "What a batch is": A^t = groups present in B^t, {A_j} its support, q_j = P[A^t = A_j]; group-blind weight pi-hat^t_i = batch share | matches FedAVOT's q over subsets; the batch-share weight is the group-blind gradient average | OK |
| S4 | "[FedAVOT Eq. 2] read at one local step" | FedAVOT (2): p~_i = sum over A containing i of q(A)/abs(A); that is the uniform-within-batch case of his Prop. 1, so the attribution is right | OK |
| S5 | Prop. 1: p~_i = sum over A containing i of q(A) E[pi-hat_i given A^t = A] | E[grad] = sum_A q(A) sum_i E[pi-hat_i given A] grad f_i (needs pi-hat independent of the sample gradients given A; true for iid draws) | OK |
| S6 | "= pi for i.i.d. sampling" | E[pi-hat_i] = pi_i unconditionally | OK |
| S7 | "= sum q(A)/abs(A) for uniform-within-batch averaging" | CAMSAP eq. (2); under K-of-N sampling this is r_i/K, exactly the p~ our floors use | OK |
| S8 | p~ is a probability vector | not stated; CAMSAP Lemma 1 proves it for the uniform case; in general sum_i p~_i = sum_A q(A) sum_i E[pi-hat_i given A] = 1 | NOTE: one clause would close it |
| S9 | abs(F_p - F_p~) <= M * l1(p - p~) | needs 0 <= f_i <= M (he says "bounded by M"); fine | OK |
| S10 | excess >= F_p(theta*_p~) - F_p(theta*), "bounded above by 2M * l1(p - p~), does not vanish with T" | two-point argument, correct | OK |
| S11 | Contributions item 1: "Group-blind minibatch SGD is agnostic FedAvg with one local step" | agnostic FedAvg (CAMSAP Alg. 1 line 5) averages UNIFORMLY over available clients, i.e. the uniform-within-batch case; the batch-share case is a weighted average. Both are covered by Prop. 1, but the sentence equates group-blind SGD with the uniform case only. Our experiments ARE the uniform-within-batch case (weights 1/K), so the experiments match the sentence | NOTE: exact for uniform-within-batch; "reduces to" would be safer than "is" |
| S12 | Notation: r_i = observation rate (first used in Contributions 2, defined in Cor. 5); pi = prevalence | consistent throughout. r_i is our inclusion probability pi_i, so any text pasted from the previous Overleaf must translate pi_i -> r_i | OK |
| S13 | Closing sentence: "tilting the sampler so that p~ = p is available only when p is reachable" | correct pointer to Sec. 3 | OK |

## Proposed edits (none required for correctness)
1. S8: after the definition of p~ in Prop. 1, add "(a probability vector, since the conditional shares sum to one for every A)". +1 line.
2. S11: "is agnostic FedAvg" -> "reduces, for uniform-within-batch averaging, to agnostic FedAvg", or leave. 0 lines.

No other change to Section 2. It matches the two reference papers' setup and is tighter than the
previous Overleaf's version; nothing from complete.tex needs to be pulled in.
