"""One-shot (2026-09-21, after fit_squeeze.py): second squeeze, Secs. 2-3 short prose, Fig. 1
caption/geometry, E3 opener, figure widths, appendix block E. Every removed clause is in the
_full sections (extended version); listed in review/CUT_LEDGER.md. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
PF = "sections/problem_formulation_short.tex"
PS = "sections/proposed_solution_short.tex"
ES = "sections/experiments_short.tex"

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

EDITS = [
 (PF, r"""$g_i(\theta)$ of $f_i$ satisfies $\E\|g_i(\theta)\|^2\le G^2$ on $\mathcal{C}$.
\end{assumption}
\noindent These are the assumptions of \cite{rahimi2025agnostic,rahimi2025fedavot}
restated for groups; they restrict neither $p$ nor $\pi$.""",
      r"""$g_i(\theta)$ of $f_i$ satisfies $\E\|g_i(\theta)\|^2\le G^2$ on $\mathcal{C}$
(the assumptions of \cite{rahimi2025agnostic,rahimi2025fedavot} restated for
groups; nothing restricts $p$ or $\pi$).
\end{assumption}"""),
 (PF, r"""$q_j\triangleq\PP[A^t=A_j]$, known or estimated offline by simulating the
sampler. The observation rate of group $i$ is
$r_i\triangleq\PP[i\in A^t]=\sum_{j:\,i\in A_j}q_j$, under i.i.d.\ sampling
$1-(1-\pi_i)^b$: a group whose prevalence is below the resolution of the
batch is absent from most batches whatever $p$ says. This is federated
learning under partial participation, with $A^t$ the participating clients,
$q$ the availability and $p$ the importance distribution
\cite{rahimi2025fedavot,rahimi2025agnostic}.""",
      r"""$q_j\triangleq\PP[A^t=A_j]$. The observation rate of group $i$ is
$r_i\triangleq\PP[i\in A^t]=\sum_{j:\,i\in A_j}q_j$, under i.i.d.\ sampling
$1-(1-\pi_i)^b$: a group whose prevalence is below the resolution of the
batch is absent from most batches whatever $p$ says. In federated terms
$A^t$ is the participating set, $q$ the availability and $p$ the importance
distribution \cite{rahimi2025fedavot,rahimi2025agnostic}."""),
 (PF, r"""The group-blind update averages the per-example subgradients of $B^t$,
giving group $i\in A^t$ the weight $\widehat{\pi}^t_i$, its share of the
batch, and absent groups zero. Averaging over the batch given $A^t$ and then
over $A^t\sim q$, the hierarchical experiment of
\cite[Eq.~4]{rahimi2025agnostic}, names the function SGD in fact minimizes.""",
      r"""The group-blind update gives group $i\in A^t$ the weight $\widehat{\pi}^t_i$,
its batch share, and absent groups zero; averaging over the batch given
$A^t$ and then over $A^t\sim q$ \cite[Eq.~4]{rahimi2025agnostic} names the
function SGD in fact minimizes."""),
 (PS, r"""with mask $E=\{(i,j): i\in A_j\}$: a group absent from the batch cannot be
weighted. Unlike classical transport \cite{villani2009,peyre2019} there is
no cost to minimize; any coupling respecting \eqref{eq:mot} serves.
Fig.~\ref{fig:mask} is the picture.""",
      r"""with mask $E=\{(i,j): i\in A_j\}$ (Fig.~\ref{fig:mask}): an absent group
cannot be weighted, and unlike classical transport
\cite{villani2009,peyre2019} there is no cost to minimize."""),
 (PS, r"""   node distance=2.4mm,
   grp/.style={draw,rounded corners=1pt,minimum width=9mm,minimum height=3.9mm,font=\tiny,fill=Periwinkle!20},
   atm/.style={draw,rounded corners=1pt,minimum width=13mm,minimum height=3.9mm,font=\tiny,fill=YellowOrange!20},""",
      r"""   node distance=1.8mm,
   grp/.style={draw,rounded corners=1pt,minimum width=9mm,minimum height=3.4mm,font=\tiny,fill=Periwinkle!20},
   atm/.style={draw,rounded corners=1pt,minimum width=13mm,minimum height=3.4mm,font=\tiny,fill=YellowOrange!20},"""),
 (PS, r"""\caption{The mask $E$. Batch compositions carry the mass $q$ they occur with;
groups must receive the mass $p$ the objective assigns them. Group $4$ is
reachable only through $A_4$, so exact alignment requires $p_4\le q_4$: the
Hall condition of Thm.~\ref{thm:feas} read on the singleton $I=\{4\}$. Shrinking
the batch deletes $A_4$ from the support and makes $p_4$ unreachable.}""",
      r"""\caption{The mask $E$: compositions carry the mass $q$ they occur with, groups
must receive the mass $p$ the objective assigns. Group $4$ is reachable only
through $A_4$, so alignment needs $p_4\le q_4$, the Hall condition of
Thm.~\ref{thm:feas} on $I=\{4\}$; a smaller batch deletes $A_4$ and makes
$p_4$ unreachable.}"""),
 (PS, r"""Existence of a coupling is a supply--demand question on the bipartite graph
$E$, settled by flow duality; proofs are in the appendix.""",
      r"""Existence is a supply--demand question on the bipartite graph $E$, settled
by flow duality (proofs in the appendix)."""),
 (PS, r"""Under i.i.d.\ sampling of $b$ examples the upper constraint reads
$b\ge\log(1-p_i)/\log(1-\pi_i)$; under $K$-of-$N$ uniform group sampling it
reads $p_i\le K/N$. The infeasible mass is the axis Sec.~\ref{sec:exp}
sweeps; feasible and infeasible regimes are its two ends.""",
      r"""Under i.i.d.\ sampling of $b$ examples the upper constraint reads
$b\ge\log(1-p_i)/\log(1-\pi_i)$, under $K$-of-$N$ group sampling
$p_i\le K/N$; $\nu$ is the axis Sec.~\ref{sec:exp} sweeps."""),
 (PS, r"""Given feasibility, a coupling is obtained by iterative proportional fitting
(Sinkhorn scaling) on the masked support
\cite{sinkhorn1967,cuturi2013,peyre2019}, rescaling rows to $p$ and columns
to $q$ in turn (appendix, \eqref{eq:ipfp}), at $O(|E|)$ per sweep with
$|E|\le NM$ and $M$ the number of \emph{realized} compositions, once,
offline; training then adds one lookup and one multiply per group per step.
Since $\mathbf{1}_N^\top T=q$ and $Y=T\mathrm{diag}(q)^{-1}$, every column
$Y[\cdot,j]$ is a probability vector on $A_j$, the property each bound
uses. Algorithm~\ref{alg:gavot} is the resulting method; $\gamma=1$ is the
risk-neutral rule analyzed here, $\gamma<1$ the layer of Sec.~\ref{sec:cvar}.""",
      r"""Given feasibility, a coupling is obtained by Sinkhorn scaling on the masked
support \cite{sinkhorn1967,cuturi2013,peyre2019} (appendix, \eqref{eq:ipfp}),
$O(|E|)$ per sweep with $M$ the number of \emph{realized} compositions,
once, offline; training then adds one lookup and one multiply per group per
step. Since $\mathbf{1}_N^\top T=q$ and $Y=T\mathrm{diag}(q)^{-1}$, every
column $Y[\cdot,j]$ is a probability vector on $A_j$, the property each
bound uses. Algorithm~\ref{alg:gavot} is the resulting method; $\gamma=1$ is
the risk-neutral rule analyzed here, $\gamma<1$ the layer of Sec.~\ref{sec:cvar}."""),
 (PS, r"""When \eqref{eq:hall} fails, Sinkhorn does not diverge: its iterates
accumulate at the coupling whose row marginal $\hat p\triangleq T\mathbf{1}$
is the KL-closest to $p$ over the reachable polytope
$\{T\mathbf{1}: T\ge 0,\ \mathbf{1}^\top T=q,\ \mathrm{supp}(T)\subseteq E\}$
\cite{csiszar1975,gietl2013ipfp,peyre2019}. The column marginal is met
exactly, so both lemmas hold with $\hat p$ for $p$: the algorithm is unbiased
SGD on the surrogate $F_{\hat p}$, and on singletons $\hat p_i\le r_i$, so
groups with $p_i>r_i$ are truncated at their observation rate.""",
      r"""When \eqref{eq:hall} fails, Sinkhorn accumulates at the coupling whose row
marginal $\hat p\triangleq T\mathbf{1}$ is KL-closest to $p$ over the
reachable polytope $\{T\mathbf{1}: T\ge 0,\ \mathbf{1}^\top T=q,\
\mathrm{supp}(T)\subseteq E\}$ \cite{csiszar1975,gietl2013ipfp,peyre2019}.
The column marginal is met exactly, so both lemmas hold with $\hat p$ for
$p$: unbiased SGD on the surrogate $F_{\hat p}$, with $\hat p_i\le r_i$ on
singletons, so groups with $p_i>r_i$ are truncated at their observation rate."""),
 (PS, r"""\noindent Both terms are available before training, $\hat p$ and $\tilde p$
from $(p,q,E)$ and $\Phi$ exactly on instances with a closed-form or convex
frontier; the gain decides the sign, the residual is a stepsize artifact
(Sec.~\ref{sec:exp}), and the $\ell_1$ bound is too loose to discriminate.""",
      r"""\noindent Both terms are available before training, $\hat p,\tilde p$ from
$(p,q,E)$ and $\Phi$ exactly on instances with a closed-form or convex
frontier; the gain decides the sign, the residual is a stepsize artifact
(Sec.~\ref{sec:exp})."""),
 (ES, r"""Table~\ref{tab:severity} and Fig.~\ref{fig:severity} are the main evidence.
On Adult the measured gain tracks""",
      r"""On Adult (Table~\ref{tab:severity}, Fig.~\ref{fig:severity}) the measured gain tracks"""),
 (ES, r"""\includegraphics[width=0.88\columnwidth]{figs/severity_imdb.pdf}""",
      r"""\includegraphics[width=0.85\columnwidth]{figs/severity_imdb.pdf}"""),
 (ES, r"""\includegraphics[width=0.95\columnwidth]{figs/rare_group_fit.pdf}""",
      r"""\includegraphics[width=0.9\columnwidth]{figs/rare_group_fit.pdf}"""),
 ("appendix.tex", r"""age; at $\beta{=}0$ nine groups are infeasible (mass $.31$), at $\beta{=}3$
forty-one ($.88$). Each step draws""",
      r"""age. Each step draws"""),
 ("appendix.tex", r"""inequalities of \eqref{eq:hall}. All rules consume the same $H{=}5$ local
updates from the same draw $A^t$; the fixed multiplier is $(m/K)\,p_i$,
the rescaling that presumes uniform observation, and full is the reference
$\Phi(p)$. $\argmin F_w$ is closed-form""",
      r"""inequalities of \eqref{eq:hall}. All rules consume the same $H{=}5$ local
updates from the same draw $A^t$. $\argmin F_w$ is closed-form"""),
]

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    print("ok")
