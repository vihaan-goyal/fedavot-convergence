import io, re
D = r"C:\Users\vihaa\fedavot-convergence\paper\gavot_draft"
ps = io.open(D + r"\proposed_solution.tex", encoding="utf-8").read()
pf = io.open(D + r"\problem_formulation.tex", encoding="utf-8").read()
NL = chr(10)

def cut_proof(src, label_anchor):
    i = src.index(label_anchor)
    a = src.index(r"\begin{proof}", i)
    b = src.index(r"\end{proof}", a) + len(r"\end{proof}")
    body = src[a:b]
    inner = re.sub(r"^\\begin\{proof\}(\[[^\]]*\])?\s*", "", body)
    inner = re.sub(r"\s*\\end\{proof\}$", "", inner)
    src = src[:a].rstrip(NL) + NL + src[b:].lstrip(NL)
    return src, inner

def rep(s, old, new):
    assert s.count(old) == 1, old[:60]
    return s.replace(old, new)

moved = {}
ps, moved["feas"] = cut_proof(ps, r"\label{thm:feas}")
ps, moved["cor"]  = cut_proof(ps, r"\label{cor:batchsize}")
ps, moved["rate"] = cut_proof(ps, r"\label{thm:rate}")
ps, moved["inf"]  = cut_proof(ps, r"\label{thm:infeasible}")

ps = rep(ps,
r"""Read on singletons, \eqref{eq:hall} becomes a statement one can act on before
training starts.""",
r"""Proofs are in the appendix. Read on singletons, \eqref{eq:hall} becomes a
statement one can act on before training starts.""")

ps = rep(ps,
r"""The constant in \eqref{eq:rate} is the one of full-participation SGD and is
independent of how many groups appear in a batch: a composition covering two
groups yields the same bound as one covering all $N$, though with larger
realized variance. No step of the proof refers to $|A^t|$; the only
properties of the estimator used are the two lemmas, which is why the rate of
\cite{rahimi2025fedavot} transfers verbatim from aggregation of models to
aggregation of gradients.""",
r"""The constant in \eqref{eq:rate} is that of full-participation SGD and is
independent of how many groups appear in a batch: a composition covering two
groups yields the same bound as one covering all $N$, though with larger
realized variance. The proof uses only the two lemmas and never refers to
$|A^t|$, which is why the rate of \cite{rahimi2025fedavot} transfers verbatim
from aggregation of models to aggregation of gradients.""")
ps = rep(ps,
r"""Theorem~\ref{thm:infeasible} replaces the usual bias \emph{bound}
\cite{rahimi2025fedavot} by an exact \emph{decomposition}. Both terms are
available before training: $\hat p$ and $\tilde p$ from $(p,q,E)$ alone, and
on instances with a closed-form or convex frontier $\Phi$ to machine
precision. The alignment gain is fixed by the instance and decides the sign of
the comparison; the residual is paid by the estimator and, as
Sec.~\ref{sec:exp} shows, is a stepsize artifact. The $\ell_1$ bound is the
weaker object and we report both, because it turns out too loose to
discriminate.""",
r"""Theorem~\ref{thm:infeasible} replaces the usual bias \emph{bound}
\cite{rahimi2025fedavot} by an exact \emph{decomposition}, both terms of which
are available before training: $\hat p$ and $\tilde p$ from $(p,q,E)$, and
$\Phi$ exactly on instances with a closed-form or convex frontier. The gain is
fixed by the instance and decides the sign of the comparison; the residual is
paid by the estimator and, as Sec.~\ref{sec:exp} shows, is a stepsize
artifact. The $\ell_1$ bound is the weaker object and we report both, because
it turns out too loose to discriminate.""")
ps = rep(ps,
r"""Corollary~\ref{cor:batchsize} says that importance may not exceed observation
rate: a rare group is reachable only if the batch is large enough to contain
it often enough. The infeasible mass $\nu$ of \eqref{eq:batchlaw} is the axis
we sweep. At $\nu=0$ exact alignment is available; as $\nu$ grows, more of $p$
sits outside the set of row marginals the mask can reach. Reporting a
\emph{feasible} and an \emph{infeasible} regime is reporting two points on
this continuum, and Sec.~\ref{sec:exp} sweeps it instead.""",
r"""Importance may not exceed observation rate: a rare group is reachable only
if the batch is large enough to contain it often enough. The infeasible mass
$\nu$ is the axis we sweep: at $\nu=0$ exact alignment is available, and as
$\nu$ grows more of $p$ sits outside the set of row marginals the mask can
reach. A \emph{feasible} and an \emph{infeasible} regime are two points on
this continuum, and Sec.~\ref{sec:exp} sweeps it instead.""")

pf = rep(pf,
r"""Proposition~\ref{prop:surrogate} says that the choice of $p$ in
\eqref{eq:target} is decorative unless the aggregation step is changed: the
iterates converge, at the usual rate, to the minimizer of a function whose
weights are induced by the sampler rather than chosen. The bias is a fixed
vector, $p-\tilde p$, and survives every stepsize schedule. Rebalancing the
sampler is only a partial fix, since $\tilde p_i\le r_i$ always holds and a
group with $p_i>r_i$ cannot be sampled into enough batches however the sampler
is tilted, while upscaling the examples that do appear by $p_i/\tilde p_i$
reintroduces an amplitude distortion that destabilizes the iterates
\cite{rahimi2025fedavot}. The question is therefore the one posed for
federated aggregation in \cite{rahimi2025fedavot}, read on batches:""",
r"""Proposition~\ref{prop:surrogate} says that the choice of $p$ in
\eqref{eq:target} is decorative unless the aggregation step is changed: the
iterates converge, at the usual rate, to the minimizer of a function whose
weights are induced by the sampler rather than chosen, and the bias
$p-\tilde p$ survives every stepsize schedule. Rebalancing the sampler is
only a partial fix: $\tilde p_i\le r_i$ always, so a group with $p_i>r_i$
cannot be sampled into enough batches however the sampler is tilted, while
upscaling the examples that do appear reintroduces an amplitude distortion
that destabilizes the iterates \cite{rahimi2025fedavot}. The question is the
one posed for federated aggregation in \cite{rahimi2025fedavot}, read on
batches:""")
pf = rep(pf,
r"""This is the situation of federated learning under partial participation:
$A^t$ is the set of participating clients, $q$ the availability distribution,
and $p$ the importance distribution \cite{rahimi2025fedavot,rahimi2025agnostic}.
We treat $q$ as known; when it is not available in closed form it is
estimated offline by simulating the sampler, as in our experiments.""",
r"""This is federated learning under partial participation: $A^t$ is the set
of participating clients, $q$ the availability distribution, $p$ the
importance distribution \cite{rahimi2025fedavot,rahimi2025agnostic}. We treat
$q$ as known; otherwise it is estimated offline by simulating the sampler, as
in our experiments.""")

io.open(D + r"\proposed_solution.tex", "w", encoding="utf-8", newline=NL).write(ps)
io.open(D + r"\problem_formulation.tex", "w", encoding="utf-8", newline=NL).write(pf)

ap = io.open(D + r"\appendix.tex", encoding="utf-8").read()
a = ap.index(r"\noindent\textbf{A. Proof of Theorem~\ref{thm:rate}.}")
b = ap.index(r"\medskip", a)
proofs = (r"\noindent\textbf{A. Proofs.}" + NL +
    r"\emph{Theorem~\ref{thm:feas} (sketch).} " + moved["feas"] + NL + NL +
    r"\noindent\emph{Corollary~\ref{cor:batchsize}.} " + moved["cor"] + NL + NL +
    r"\noindent\emph{Theorem~\ref{thm:rate}.} " + moved["rate"] + NL +
    r"In full: $\E\|\theta^{t}-\theta^\star\|^2\le\E\|\theta^{t-1}-\theta^\star\|^2-2\eta\,\E[F_p(\theta^{t-1})-F_p(\theta^\star)]+\eta^2G^2$;" + NL +
    r"summing over $t\le T$, telescoping, dropping the terminal distance and applying Jensen to $\bar\theta_T$ gives" + NL +
    r"$\E F_p(\bar\theta_T)-F_p(\theta^\star)\le D^2/(2\eta T)+\eta G^2/2$, which is $DG/\sqrt{T}$ at $\eta=D/(G\sqrt{T})$;" + NL +
    r"the same bound holds for $\eta_t=\eta_0/\sqrt{t}$ up to constants." + NL + NL +
    r"\noindent\emph{Theorem~\ref{thm:infeasible}.} " + moved["inf"] + NL + NL)
ap = ap[:a] + proofs + ap[b:]
io.open(D + r"\appendix.tex", "w", encoding="utf-8", newline=NL).write(ap)
print("moved", {k: len(v) for k, v in moved.items()})
