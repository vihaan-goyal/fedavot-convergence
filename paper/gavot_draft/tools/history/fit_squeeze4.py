"""One-shot (2026-09-21, after fit_squeeze3.py): fourth squeeze (last ~13 lines): abstract clause,
Sec. 4 composition sentence, Algorithm 1 Require line, Sec. 2 FL sentence (already in Sec. 1),
Table 1 caption, E3 overfull line, E4 closing line, tighter float spacing. Every removed clause is
in the _full sections; listed in review/CUT_LEDGER.md. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
PF = "sections/problem_formulation_short.tex"
PS = "sections/proposed_solution_short.tex"
ES = "sections/experiments_short.tex"
MF = "main_fit.tex"

def sub(rel, old, new, count=1):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == count, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

EDITS = [
 (MF, r"""prevalence-weighted surrogate rather than to the target risk. A minibatch is a
partial-participation event over groups, which makes group-fair training an
instance of federated aggregation under availability skew, and we carry the
masked optimal transport construction of \textsf{FedAVOT} across. Aligning the""",
      r"""prevalence-weighted surrogate rather than to the target risk. A minibatch is a
partial-participation event over groups, so we carry the masked optimal
transport construction of \textsf{FedAVOT} across. Aligning the"""),
 (MF, r"""jointly convex, with subgradients in both arguments again $p$-weighted sums of
per-group quantities, so Lemma~\ref{lem:unbiased} applies unchanged. This is why
the layers compose rather than interfere: transport fixes \emph{which}
distribution the expectation is under, CVaR changes \emph{what} is averaged.
Lines 6 and 8 of Algorithm~\ref{alg:gavot} implement \eqref{eq:ru}.""",
      r"""jointly convex, with subgradients in both arguments $p$-weighted sums of
per-group quantities, so Lemma~\ref{lem:unbiased} applies unchanged: transport
fixes \emph{which} distribution the expectation is under, CVaR \emph{what} is
averaged (lines 6 and 8 of Algorithm~\ref{alg:gavot})."""),
 (PS, r"""\Require target $p$, composition law $(q,\{A_j\},E)$, step $\eta$, horizon $T$,
 CVaR parameters $(\alpha,\gamma)$ with $\gamma=1$ for the risk-neutral method""",
      r"""\Require $p$; $(q,\{A_j\},E)$; $\eta$; $T$; $(\alpha,\gamma)$, $\gamma=1$ risk-neutral"""),
 (PF, r"""batch is absent from most batches whatever $p$ says. In federated terms
$A^t$ is the participating set, $q$ the availability and $p$ the importance
distribution \cite{rahimi2025fedavot,rahimi2025agnostic}.""",
      r"""batch is absent from most batches whatever $p$ says."""),
 (ES, r"""\caption{Headline cells, tail-500 over $5$ seeds, decaying stepsize. \emph{full}
sees every group every step; \emph{upsamp.}, self-normalized upsampling
(weights $\propto p_i/r_i$ within the batch); LDS, label-distribution
smoothing \cite{yang2021dir}, regression only. The fixed multiplier $m/K$
diverges whenever observation rates are non-uniform.}""",
      r"""\caption{Headline cells, tail-500 over $5$ seeds, decaying stepsize. \emph{full}:
every group every step; \emph{upsamp.}: weights $\propto p_i/r_i$ within the
batch; LDS \cite{yang2021dir}: label-distribution smoothing, regression only;
$m/K$ diverges under non-uniform observation.}"""),
 (ES, r"""$-0.03$): Theorem~\ref{thm:infeasible} at finite $T$. The $\ell_1$
criterion cannot do this: $\|p-\hat p\|_1<\|p-\tilde p\|_1$ holds in all
eleven instances, including the three where transport loses or ties.""",
      r"""$-0.03$): Theorem~\ref{thm:infeasible} at finite $T$. The $\ell_1$ criterion
cannot: $\|p-\hat p\|_1<\|p-\tilde p\|_1$ in all eleven instances, the three
where transport loses or ties included."""),
 (ES, r"""dashed floors, and what remains is the residual, $2.3$ at $\nu{=}.88$, the
one significant loss. Transport helps exactly while there is mass left to move.""",
      r"""dashed floors, and what remains is the residual, $2.3$ at $\nu{=}.88$, the
one significant loss."""),
 (ES, r"""until the floors close at high $\nu$; the sign is set by \eqref{eq:infeasible}.}""",
      r"""until the floors close at high $\nu$.}
\vspace{-6pt}"""),
 (ES, r"""once $\beta>0$. Same runs as Table~\ref{tab:overall}.}""",
      r"""once $\beta>0$. Same runs as Table~\ref{tab:overall}.}
\vspace{-6pt}"""),
]

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    print("ok")
