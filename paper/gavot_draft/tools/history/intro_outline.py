"""One-shot (2026-09-21): Herlock replaced the Introduction on his Overleaf with a four-line
outline (what imbalanced regression/classification is; what SGD does to critical groups, with a
simple calculation; the usual up/down-sampling remedy; a survey of other algorithms) and added
Amtej and Vihaan to the author line. This rewrites Sec. 1 of main_fit.tex to that outline within
the same line budget (his previous Sec. 1 text survives in original/main.tex and main_full.tex),
and takes his author line (typo "dfionysis" corrected). Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF = ROOT / "main_fit.tex"

AUTH_OLD = r"""\name{Herlock (SeyedAbolfazl) Rahimi \qquad Dionysis Kalogerias%"""
AUTH_NEW = r"""\name{Herlock (SeyedAbolfazl) Rahimi \qquad Amtej Sodhi \qquad Vihaan Goyal \qquad Dionysis Kalogerias%"""

INTRO_NEW = r"""\section{Introduction}
% =====================================================================

\noindent\textbf{Imbalanced learning.}
In imbalanced classification and imbalanced regression the training data
over-represent some groups and starve others: patients of one demographic,
faces of one age range, incomes of one race \cite{buolamwini2018gender,%
hashimoto2018repeated,sagawa2020dro,yang2021dir}. Call the groups one cares
about \emph{critical}. The objective is then not the empirical risk but
$F_p(\theta)=\sum_i p_i f_i(\theta)$, with $f_i$ the risk on group $i$ and $p$
the weighting one actually wants: uniform, inverse to prevalence, or externally
dictated \cite{mohri2019agnostic,li2020fair}.

\noindent\textbf{What SGD does to a critical group.}
Minibatch SGD never sees $p$. A batch $B^t$ of $b$ i.i.d.\ examples contains
group $i$ in proportion to its prevalence $\pi_i$, so the group-blind update
descends the prevalence-weighted risk:
\begin{equation}
\E\Big[\tfrac1b\!\sum_{(x,y)\in B^t}\!\nabla\ell(m(x;\theta),y)\Big]
=\sum_i\pi_i\nabla f_i(\theta)=\nabla F_\pi(\theta).
\label{eq:introbias}
\end{equation}
The loss surface is tilted toward the represented groups, and the tilt is a
bias, a fixed vector $\pi-p$ that survives $T\to\infty$ and every stepsize
schedule; Sec.~\ref{sec:setup} generalizes \eqref{eq:introbias} to any
sampler. A group whose prevalence is below the resolution of the batch is
absent from most batches, whatever $p$ says.

\noindent\textbf{The usual remedies.}
The standard response is to up-sample the rare groups or down-sample the
common ones and then run SGD as usual. Tilting the sampler can only move the
observation rate $r_i$ of a group up to the batch's coverage, so it cannot
help a group with $p_i>r_i$; re-weighting the examples that do appear, the
reweighting form of up-sampling, is a one-shot heuristic for a marginal
problem this paper solves exactly, and its un-normalized form, the fixed
multiplier that presumes uniform observation, destabilizes the iterates
\cite{rahimi2025fedavot}. Label-distribution smoothing \cite{yang2021dir}
re-weights by label rarity, not by how rarely a group is observed.

\noindent\textbf{Other algorithms.}
Reduction methods for group fairness return randomized mixtures or carry an
approximation constant tied to a fixed class
\cite{agarwal2018reductions,cotter2019twoplayer,chamon2020pacc};
distributionally robust and worst-group objectives
\cite{sagawa2020dro,hashimoto2018repeated,levy2020large} change the functional
rather than the sampler and are complementary (our CVaR layer is one, on top
of transport rather than instead of it); importance sampling for SGD
\cite{rizk2021importance,katharopoulos2018not} corrects variance, not the
identity of the minimized objective. The same mismatch is the central object
of federated learning, where the \emph{availability distribution} $q$ over
participating clients rarely matches the \emph{importance distribution} $p$,
so \textsf{FedAvg} optimizes a surrogate whose weights are induced rather
than chosen \cite{rahimi2025agnostic,wang2020objective,cho2022biased};
\textsf{FedAVOT} \cite{rahimi2025fedavot} removes it by a masked optimal
transport (MOT) problem on the client-round pairs that occurred. A minibatch
is a participation event: the groups in $B^t$ are the active set, its law is
$q$, and the weighting one wants is $p$. Group-fair SGD is federated
aggregation with the federation collapsed onto one machine. We call the
method \avot{} and keep the \textsf{FedAVOT} label in figures, the rule being
unchanged.

\noindent\textbf{Contributions.}"""

if __name__ == "__main__":
    s = MF.read_text(encoding="utf-8")
    assert s.count(AUTH_OLD) == 1
    s = s.replace(AUTH_OLD, AUTH_NEW)
    a = s.index("\\section{Introduction}")
    b = s.index("\\noindent\\textbf{Contributions.}")
    s = s[:a] + INTRO_NEW + s[b + len("\\noindent\\textbf{Contributions.}"):]
    # the old Related work paragraph now duplicates "Other algorithms": drop it
    c = s.index("\\noindent\\textbf{Related work.}")
    d = s.index("\\input{sections/problem_formulation_short}")
    s = s[:c] + s[d:]
    MF.write_text(s, encoding="utf-8", newline="\n")
    print("ok")
