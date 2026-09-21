"""One-shot (2026-09-21, after fit_squeeze2.py): third squeeze (last ~18 lines): Analysis lead-in,
Thm. 7 closing, Table 2 caption, Prop. 2 closing paragraph, Cor. 4 wording, Sec. 2 opener,
E1/E2/E5/protocol one-liners, figure widths, Fig. 1 spacing. Every removed clause is in the
_full sections; listed in review/CUT_LEDGER.md. Record only; already applied."""
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
 (PS, r"""Let $\hat g(\theta)=\sum_{i\in A^t}Y[i,j(t)]\,g_i(\theta)$ be the
transport-weighted batch subgradient of Algorithm~\ref{alg:gavot}, $g_i$ the
stochastic subgradient of $f_i$ from $B^t\cap$ group $i$. Everything rests on
\cite[Lem.~1]{rahimi2025fedavot} moved from models to gradients: transport
removes bias; it is not a variance reduction device.""",
      r"""Let $\hat g(\theta)=\sum_{i\in A^t}Y[i,j(t)]\,g_i(\theta)$ be the
transport-weighted batch subgradient of Algorithm~\ref{alg:gavot}. Everything
rests on \cite[Lem.~1]{rahimi2025fedavot} moved from models to gradients:
transport removes bias, it is not a variance reduction device."""),
 (PS, r"""The constant is that of full-participation SGD, independent of how many
groups a batch covers, though the realized variance is larger.""",
      r"""The constant is that of full-participation SGD, independent of batch coverage."""),
 (PS, r"""Feasibility of \eqref{eq:mot} requires $\PP[A^t=\{i\}]\le p_i\le r_i$ for every
$i$, with $r_i=\PP[i\in A^t]$ the observation rate of Sec.~\ref{sec:setup}.
Writing""",
      r"""Feasibility of \eqref{eq:mot} requires $\PP[A^t=\{i\}]\le p_i\le r_i$ for every
$i$, with $r_i$ the observation rate. Writing"""),
 (PS, r"""   node distance=1.8mm,""", r"""   node distance=1.5mm,"""),
 (ES, r"""\caption{IMDb-Wiki severity sweep, decaying stepsize. $\Delta_{\mathrm{floor}}$
is the alignment gain of Theorem~\ref{thm:infeasible}, \emph{gain} the measured
advantage of transport, $t$ its Welch statistic (population std). The excess
residual transport pays averages $1.9$; the sign flips where
$\Delta_{\mathrm{floor}}$ crosses it. Adult skews: appendix.}""",
      r"""\caption{IMDb-Wiki severity sweep, decaying stepsize: $\Delta_{\mathrm{floor}}$
the alignment gain of Theorem~\ref{thm:infeasible}, \emph{gain} the measured
advantage of transport, $t$ its Welch statistic. The residual averages $1.9$;
the sign flips where $\Delta_{\mathrm{floor}}$ crosses it. Adult: appendix.}"""),
 (PF, r"""Empirical risk minimization weights the
groups by prevalence, $F_\pi=\sum_i\pi_i f_i$, so a majority group dominates
the trained model. The remedy is to fix an \emph{importance distribution}""",
      r"""Empirical risk minimization weights
groups by prevalence, $F_\pi=\sum_i\pi_i f_i$; the remedy is to fix an
\emph{importance distribution}"""),
 (PF, r"""\noindent (Proof in the appendix.) The choice of $p$ in \eqref{eq:target}
is thus decorative unless the aggregation step changes: the bias
$p-\tilde p$ survives every stepsize schedule, rebalancing the sampler
cannot help a group with $p_i>r_i$ since $\tilde p_i\le r_i$ always, and
upscaling the examples that do appear destabilizes the iterates
\cite{rahimi2025fedavot}. The question of \cite{rahimi2025fedavot}, read on
batches: \emph{can the per-batch group weights be chosen so that SGD driven
by $q$ converges for the objective defined by $p$?}""",
      r"""\noindent (Proof in the appendix.) The choice of $p$ is thus decorative
unless the aggregation step changes: the bias $p-\tilde p$ survives every
stepsize schedule, rebalancing the sampler cannot help a group with $p_i>r_i$
since $\tilde p_i\le r_i$ always, and upscaling the examples that do appear
destabilizes the iterates \cite{rahimi2025fedavot}. The question, read on
batches: \emph{can the per-batch group weights be chosen so that SGD driven
by $q$ converges for the objective defined by $p$?}"""),
 (ES, r"""(per-race table in the appendix: transport improves four races of five and
regresses only the majority). On the least represented group the layer never
helps:""",
      r"""(per-race table in the appendix). On the least represented group the layer
never helps:"""),
 (ES, r"""$30$-image group, $\pm5$ to $10$ across seeds). The rare-group loss tells
the same story as the objective, more sensitively.""",
      r"""$30$-image group, $\pm5$ to $10$ across seeds)."""),
 (ES, r"""steps, $5$ seeds, $F_p$ over the last $500$ steps. Floors are exact
(appendix, with the full protocol and the closed-form check); the extended
version carries the unabridged discussion.""",
      r"""steps, $5$ seeds, $F_p$ over the last $500$ steps. Floors are exact; full
protocol and closed-form check in the appendix, unabridged discussion in the
extended version."""),
 (ES, r"""Table~\ref{tab:overall} reports the four instances a practitioner would
recognize. Transport wins on three:""",
      r"""Table~\ref{tab:overall} reports the four headline instances. Transport wins
on three:"""),
 (ES, r"""\includegraphics[width=0.85\columnwidth]{figs/severity_imdb.pdf}""",
      r"""\includegraphics[width=0.82\columnwidth]{figs/severity_imdb.pdf}"""),
 (ES, r"""\includegraphics[width=0.9\columnwidth]{figs/rare_group_fit.pdf}""",
      r"""\includegraphics[width=0.86\columnwidth]{figs/rare_group_fit.pdf}"""),
]

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    print("ok")
