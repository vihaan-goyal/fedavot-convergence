"""One-shot (2026-09-21): apply review/HERLOCK_TRIM_SUGGESTIONS.md to main_fit.tex (abstract,
Groups-as-clients, Contributions 2+3 merged, Related work, Sec. 4 closing paragraph, Conclusion),
plus the Table 1 label squeeze and the shorter E1/protocol wording in experiments_short.tex.
Herlock asked (9/21) for all changes to go on the Overleaf, so the fit build must be 4 pages.
No claim or number is changed. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

ABS_OLD = r"""Minibatch SGD is group-blind. Which groups appear in a batch is decided by how
often they occur in the data, not by how much they are meant to count in the
objective, and when the two disagree the iterates converge to a
prevalence-weighted surrogate rather than to the target risk. The gap is a bias,
so no amount of training removes it. A minibatch is a partial-participation
event over groups, which makes group-fair training an instance of federated
aggregation under availability skew, and we carry the masked optimal transport
construction of \textsf{FedAVOT} across. Aligning the
batch-composition distribution $q$ with the target importance distribution $p$
produces per-batch group weights whose induced stochastic subgradient is exactly
unbiased for the target risk, giving the standard $O(1/\sqrt{T})$ rate in the
nonsmooth convex regime with a constant that does not depend on how many groups
a batch happens to cover. Exact alignment is feasible precisely under a Hall-type condition, which reduces
to the per-group requirement that importance not exceed observation rate; past
it Sinkhorn returns an information projection and a residual we compute in
closed form rather than bound. That closed form turns the excess risk into two
terms, an alignment gain fixed by the instance and an optimization residual paid
by the estimator, and a severity sweep over eleven availability skews on Adult
and IMDb-Wiki shows the two crossing: transport wins while the gain exceeds the
residual and loses past it, at a threshold the decomposition locates in advance.
The residual is a stepsize artifact, not a property of the method, and a
decaying schedule removes it on every instance where it had reversed the sign.
A mean--CVaR layer composed on top reaches the worst group at rate
$O(\kappa(\alpha,\gamma)/\sqrt{T})$."""
ABS_NEW = r"""Minibatch SGD is group-blind: which groups appear in a batch is decided by
their prevalence in the data, not by how much they are meant to count in the
objective, and when the two disagree the iterates converge to a
prevalence-weighted surrogate rather than to the target risk. A minibatch is a
partial-participation event over groups, which makes group-fair training an
instance of federated aggregation under availability skew, and we carry the
masked optimal transport construction of \textsf{FedAVOT} across. Aligning the
batch-composition law $q$ with the target importance $p$ yields per-batch group
weights whose stochastic subgradient is exactly unbiased for the target risk,
with the standard $O(1/\sqrt{T})$ rate and a constant independent of batch
coverage. Alignment is feasible under a Hall-type condition that reduces to
importance not exceeding observation rate; past it, Sinkhorn returns an
information projection whose residual we compute in closed form, splitting the
excess risk into an alignment gain fixed by the instance and an optimization
residual paid by the estimator. A severity sweep over eleven availability skews
on Adult and IMDb-Wiki shows the two crossing where the decomposition predicts;
the residual is a stepsize artifact a decaying schedule removes. A mean--CVaR
layer composed on top reaches the worst group at rate
$O(\kappa(\alpha,\gamma)/\sqrt{T})$."""

GROUPS_OLD = r"""The same mismatch is the central object of a different literature. In federated
learning the \emph{availability distribution} $q$ over which clients participate
in a round rarely matches the \emph{importance distribution} $p$ that defines
the objective, and \textsf{FedAvg} consequently optimizes a surrogate whose
weights are induced by the availability process rather than chosen
\cite{rahimi2025agnostic,wang2020objective,cho2022biased}. \textsf{FedAVOT}
\cite{rahimi2025fedavot} removes that mismatch by posing aggregation as a masked
optimal transport (MOT) problem: find a coupling whose column marginal is the
availability law and whose row marginal is the target $p$, supported only on
client-round pairs that actually occurred. The observation driving this paper is that a minibatch is a participation
event: the groups represented in $B^t$ are the active set $S^t$, its law is $q$,
and the weighting one wants is $p$. Group-fair SGD is federated aggregation with
the federation collapsed onto one machine. We call the method \avot{} and keep
the \textsf{FedAVOT} label in figures, the aggregation rule being unchanged."""
GROUPS_NEW = r"""The same mismatch is the central object of federated learning, where the
\emph{availability distribution} $q$ over participating clients rarely matches
the \emph{importance distribution} $p$ defining the objective, so
\textsf{FedAvg} optimizes a surrogate whose weights are induced rather than
chosen \cite{rahimi2025agnostic,wang2020objective,cho2022biased};
\textsf{FedAVOT} \cite{rahimi2025fedavot} removes it by a masked optimal
transport (MOT) problem, a coupling of the availability law with the target $p$
supported on the client-round pairs that occurred. A minibatch is a
participation event: the groups in $B^t$ are the active set $S^t$, its law is
$q$, and the weighting one wants is $p$. Group-fair SGD is federated
aggregation with the federation collapsed onto one machine. We call the method
\avot{} and keep the \textsf{FedAVOT} label in figures, the rule being unchanged."""

CONTRIB_OLD = r"""\item \emph{A coverage law and a severity measure} (Cor.~\ref{cor:batchsize}).
Feasibility is Hall-type and reduces on singletons to $p_i\le r_i$, importance
below observation rate, so the \emph{infeasible mass}
$\nu\triangleq\sum_{i:p_i>r_i}p_i$ is the natural severity axis, computable
before training.
\item \emph{A two-term decomposition that locates the crossover}
(Thm.~\ref{thm:infeasible}, Sec.~\ref{sec:exp}). Past the Hall condition the
excess splits into an \emph{alignment gain} $\Delta_{\mathrm{floor}}$, the
distance between the two optima each rule actually converges to, and an
optimization residual. The gain is exact and instance-fixed; the residual is
paid by the estimator. We sweep eleven skews and watch the two cross."""
CONTRIB_NEW = r"""\item \emph{A coverage law, a severity measure, and the crossover}
(Cor.~\ref{cor:batchsize}, Thm.~\ref{thm:infeasible}, Sec.~\ref{sec:exp}).
Feasibility is Hall-type and reduces on singletons to $p_i\le r_i$, so the
\emph{infeasible mass} $\nu\triangleq\sum_{i:p_i>r_i}p_i$ orders instances
before training; past it the excess splits into an exact, instance-fixed
\emph{alignment gain} $\Delta_{\mathrm{floor}}$, the distance between the two
optima the rules converge to, and an optimization residual paid by the
estimator. We sweep eleven skews and watch the two cross."""

RELATED_OLD = r"""Reduction methods for group fairness return randomized mixtures or carry an
approximation constant tied to a fixed class
\cite{agarwal2018reductions,cotter2019twoplayer,chamon2020pacc}.
Distributionally robust and worst-group objectives
\cite{sagawa2020dro,hashimoto2018repeated,levy2020large} change the functional
rather than the sampler and are complementary: our CVaR layer is one such
functional, obtained on top of transport rather than instead of it. Importance
sampling for SGD \cite{rizk2021importance,katharopoulos2018not} corrects
variance, not the identity of the minimized objective."""
RELATED_NEW = r"""Reduction methods for group fairness return randomized mixtures or carry an
approximation constant tied to a fixed class
\cite{agarwal2018reductions,cotter2019twoplayer,chamon2020pacc};
distributionally robust and worst-group objectives
\cite{sagawa2020dro,hashimoto2018repeated,levy2020large} change the functional
rather than the sampler and are complementary (our CVaR layer is one, on top of
transport rather than instead of it); importance sampling for SGD
\cite{rizk2021importance,katharopoulos2018not} corrects variance, not the
identity of the minimized objective."""

SEC4_OLD = r"""Both $\gamma=1$ and $\alpha=1$ recover Theorem~\ref{thm:rate} exactly, so the
grid contains the risk-neutral method along two edges, visible as the constant
row and column of every heatmap below. Sending $\alpha\downarrow 0$ drives
\eqref{eq:meancvar} to the worst group at the cost
$\kappa(\alpha,\gamma)\to\infty$: the parameter prices robustness in the
convergence constant, not in the limit."""
SEC4_NEW = r"""Both $\gamma=1$ and $\alpha=1$ recover Theorem~\ref{thm:rate} exactly; sending
$\alpha\downarrow 0$ drives \eqref{eq:meancvar} to the worst group at the cost
$\kappa(\alpha,\gamma)\to\infty$: the parameter prices robustness in the
convergence constant, not in the limit."""

CONC_OLD = r"""Group-fair training fails in a specific and fixable place: the aggregation step,
blind to the weighting the objective declares. Reading a minibatch as a
partial-participation event makes the fix the masked transport problem that
corrects availability skew in federated learning, with the same feasibility
characterization, an $O(1/\sqrt{T})$ guarantee free of batch coverage, and a
coverage law whose infeasible mass $\nu$ orders instances by severity. Past
feasibility the excess splits cleanly, into an alignment gain fixed by the
instance and an optimization residual paid by the estimator, and a sweep over
eleven skews shows the two crossing where the decomposition says they will. Transport is
worth applying while the gain exceeds the residual, both are computable before
training, and the residual is a stepsize artifact a decaying schedule removes.
The nonconvex case remains open."""
CONC_NEW = r"""Group-fair training fails in a specific and fixable place: the aggregation step,
blind to the weighting the objective declares. Reading a minibatch as a
partial-participation event makes the fix the masked transport problem of
federated learning, with its feasibility characterization, an $O(1/\sqrt{T})$
guarantee free of batch coverage, and a coverage law whose infeasible mass
$\nu$ orders instances by severity. Transport is worth applying while the
alignment gain exceeds the optimization residual, both computable before
training, and the residual is a stepsize artifact a decaying schedule removes.
The nonconvex case remains open."""

# ours: Table 1 labels, E1 baseline sentence, protocol parenthetical (short version only)
TAB_LABELS = [
    ("Adult prev.\\ ($\\nu{=}.60$) &", "Adult, $\\nu{=}.60$ &"),
    ("Adult align.\\ ($\\nu{=}0$) &", "Adult, $\\nu{=}0$   &"),
    ("IMDb skew ($\\nu{=}.31$)   &", "IMDb, $\\nu{=}.31$  &"),
    ("IMDb align.\\ ($\\nu{=}0$)  &", "IMDb, $\\nu{=}0$    &"),
]
E1_OLD = r"""Self-normalized upsampling, the reweighting form of oversampling rare
groups, recovers most of the gain and transport the rest: $0.2288$
($t{=}5.8$ against transport) and $86.74$ ($t{=}2.6$). Downsampling
($\min(p_i/r_i,1)$, normalized) is never better than upsampling, and
label-distribution smoothing \cite{yang2021dir}, which reweights by label
rarity rather than by group observation, trails even group-blind averaging.
On the least represented group the margin over upsampling widens: $77.0$
against $80.0$ and $73.6$ against $75.6$ on IMDb-Wiki."""
E1_NEW = r"""Self-normalized upsampling, the reweighting form of oversampling rare
groups, recovers most of the gain and transport the rest ($t{=}5.8$ and
$2.6$ against it); downsampling never beats it, and LDS, which reweights by
label rarity rather than by group observation, trails even group-blind
averaging. On the least represented group the margin over upsampling widens
($77.0$ against $80.0$, $73.6$ against $75.6$ on IMDb-Wiki)."""
PROTO_OLD = r"""Stepsize $\eta_t=\eta/(1+t/1000)$
unless stated, fixed before the comparison and shared by every rule (a
faster decay widens the IMDb-Wiki gap, a constant stepsize narrows it, the
winner never changes; extended version), $4000$ steps, $5$ seeds, $F_p$ over
the last $500$ steps, mean $\pm$ std."""
PROTO_NEW = r"""Stepsize $\eta_t=\eta/(1+t/1000)$
unless stated, fixed before the comparison and shared by every rule (faster
decays widen the IMDb-Wiki gap, never flip a winner; extended version),
$4000$ steps, $5$ seeds, $F_p$ over the last $500$ steps, mean $\pm$ std."""

if __name__ == "__main__":
    for old, new in ((ABS_OLD, ABS_NEW), (GROUPS_OLD, GROUPS_NEW), (CONTRIB_OLD, CONTRIB_NEW),
                     (RELATED_OLD, RELATED_NEW), (SEC4_OLD, SEC4_NEW), (CONC_OLD, CONC_NEW)):
        sub("main_fit.tex", old, new)
    for f in ("sections/experiments_short.tex", "sections/experiments_full.tex"):
        for old, new in TAB_LABELS:
            sub(f, old, new)
    sub("sections/experiments_short.tex", E1_OLD, E1_NEW)
    sub("sections/experiments_short.tex", PROTO_OLD, PROTO_NEW)
    print("ok")
