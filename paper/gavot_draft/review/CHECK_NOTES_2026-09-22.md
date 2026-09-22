# Herlock's %%CHECK notes (Overleaf revision 2026-09-22), checked against the code

Code = `scripts/pipeline/run_experiments.py` (engine `grid_local_step` / `run_unit`), sweep =
`scripts/pipeline/severity_sweep.sh` -> `results/2026-09-14_severity_sweep/`. Line numbers are
Herlock's `main.tex` (synced in 6b1b155).

## L202 FedeRage's role
arXiv:2609.21057 (Rahimi, Kalogerias), "FedeRage: Provably Convergent Agnostic Federated
Learning under General Client Drift": a risk-averse FedAvg that embeds CVaR in the local
objective, agnostic to the (unknown, drifting) participation law. So it is NOT a second
transport method; it is the participation-agnostic, CVaR counterpart. Suggested text:

    \textsf{FedeRage} \cite{rahimi2026federage} is robust to it without knowing
    the participation law, by a CVaR local objective; \textsf{FedAVOT}
    \cite{rahimi2025fedavot} corrects it exactly by a masked optimal transport
    (MOT) problem.

## L353 Alg. 1: tau projection and iterate averaging
Code does NEITHER:
- tau is not projected (no clip; starts at `--t0 0`), and its step uses a fixed `eta_t`
  (DATASET_ETA_T), not the decaying eta_t of theta. theta is not projected onto C either
  (unconstrained). Irrelevant for every gamma=1 number (all headline results); only the
  CVaR grid paragraph uses tau.
- No averaging: each step we evaluate F_p at the last iterate theta^t; "F_p over the last 500"
  = (1/500) sum_t F_p(theta^t). By convexity this UPPER-bounds F_p(average of those iterates),
  so the reported numbers are conservative relative to the Ensure line.
- Matches: per-group weights w_i = W[i,j](gamma + (1-gamma)c_i/alpha) (code applies the
  multiplier inside the local step, then averages with W[:,j]); tau aggregate
  sum_i W[i,j] tau_i equals line 348's update exactly at H=1 because W[:,j] sums to 1.
Suggested: keep Alg. 1 as the analyzed method; add to the protocol sentence
"we report the mean of $F_p$ over the last $500$ iterates, which by convexity upper-bounds
$F_p$ at their average."

## L407 KL direction
Numerical test (6 groups, K=2, 12 random infeasible instances, IPFP run 60k iterations, both
projections solved over the reachable set with SLSQP, several restarts):
p_hat = argmin_{x in Reach} KL(x || p) to 6 decimals in 12/12; in 2/12 KL(p || .) has a strictly
lower minimum than at p_hat. So the direction is the I-projection of p onto Reach, Csiszar's
sense (min D(Q||P) over Q in the set). Write it explicitly:
    $\hat p=\arg\min_{x\in\Reach}\mathrm{KL}(x\,\|\,p)$
Not verified here: that gietl2013ipfp states exactly this for the limiting ROW marginal of the
column-fitted plan; Herlock should check the theorem he is citing.

## L478 plug-in bias of 1{f_hat > tau}
In the code f_hat_i is the group's full-batch loss over all its 30 samples (Adult and IMDb-Wiki
both use samples_per_user=30), and the objective F_p is that same training loss. So the
indicator uses the exact f_i: no plug-in bias in our experiments. Caveat: for inner steps
2..H it is evaluated at the local iterate, not theta^{t-1} (exact at H=1). Suggested:
"(in our experiments $\hat f^t_i$ is the full group loss, so the indicator is exact)."

## L524 H=5, and "drawn prop. to r"
- H: yes, H=5 (`--local-epochs` default 5, not overridden in the sweep); each is a full-batch GD
  step on the group's 30 samples at lr_t, then the rule's weighted average of the 3 resulting
  models. Rerunning everything at H=1 changes every number in the paper two days out; keep the
  sentence and add "($H{=}1$ is the setting of Theorem 1; the weights, and so which weighting
  is targeted, are unchanged)". Option: a cheap H=1 check on the two end cells (IMDb beta=0
  and beta=3, decay) to confirm the ranking holds, ~20 min.
- r: two different things share the letter. The code draws K groups WITHOUT replacement
  (Gumbel top-K) with sampling weights s_i ∝ i^beta (IMDb) or ∝ p_i^beta (Adult); the
  observation rate r_i = P(i in A^t) that the rest of the paper uses (p_tilde_i = r_i/K,
  truncation at r_i, upsampling p_i/r_i -- the code uses exactly p/pi) is NOT proportional to s.
  Suggested: "the sampler draws $K{=}3$ groups without replacement with weights
  $s_i\propto p_i^\beta$ (Adult) or $s_i\propto i^\beta$ (IMDb-Wiki); $r_i$ is the resulting
  observation rate."

## L527 instance count
12 is right: Adult beta in {0, 1/4, 1/2, 3/4, 1} (beta=1 IS the aligned Adult instance, don't
count it twice) + IMDb-Wiki beta in {0, 1/2, 1, 3/2, 2, 3} + aligned IMDb-Wiki (r ∝ 101-i),
all run with decay (results/2026-09-14_severity_sweep/*_decay1000, imdb_feasible_decay1000).

## L610 "by up to 7.9"
It is MSE, and the match with Table 2's t = -7.9 is a coincidence. Constant stepsize, gain of
GAVOT over group-blind (5 seeds, Welch t):

| beta | 0 | 0.5 | 1 | 1.5 | 2 | 3 |
|---|---|---|---|---|---|---|
| gain (MSE) | -0.87 | -3.10 | -3.40 | -5.26 | -5.52 | -7.94 |
| t | -2.5 | -8.9 | -7.5 | -9.7 | -10.0 | -20.6 |

Decay values reproduce Table 2 exactly (+5.57/20.7 ... -2.28/-7.9). Note beta=0 at constant
stepsize is not significant (|t|<2.8), so "loses on all six" is true of the means only.
Suggested: "transport loses on all six IMDb-Wiki skews, by up to $7.9$ in MSE at $\beta{=}3$
(five significantly),".
