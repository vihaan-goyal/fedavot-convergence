import io
p = r"C:\Users\vihaa\fedavot-overleaf-v2-work\main.tex"
s = io.open(p, encoding="utf-8").read()
n = 0
def rep(old, new, tag):
    global s, n
    assert s.count(old) == 1, f"{tag}: found {s.count(old)}x"
    s = s.replace(old, new); n += 1

# ---- Section 2 (S8, S11)
rep(r"""$\tilde p_i=\sum_{A\ni i}q(A)\E[\widehat{\pi}^t_i\mid A^t=A]$, which is $\pi$
for i.i.d.\ sampling and $\sum_{A\ni i}q(A)/|A|$ for uniform-within-batch
averaging.""",
r"""$\tilde p_i=\sum_{A\ni i}q(A)\E[\widehat{\pi}^t_i\mid A^t=A]$ (a probability
vector, the conditional shares summing to one for every $A$), which is $\pi$
for i.i.d.\ sampling and $\sum_{A\ni i}q(A)/|A|$ for uniform-within-batch
averaging.""", "S8")
rep(r"""Group-blind minibatch SGD is
agnostic \textsf{FedAvg} with one local step, so""",
r"""Group-blind minibatch SGD reduces, under
uniform-within-batch averaging, to agnostic \textsf{FedAvg} with one local step, so""", "S11")

# ---- Section 3 (A17, A16, A15, A13)
rep(r"""Both terms of \eqref{eq:infeasible} are available before training: $\hat p$ and
$\tilde p$ from $(p,r,E)$, and on instances with a closed-form frontier
$\Phi$ exactly.""",
r"""Both terms of \eqref{eq:infeasible} are available before training: $\hat p$ and
$\tilde p$ from $(p,q,E)$, and on instances with a closed-form frontier
$\Phi$ exactly.""", "A17")
rep(r"""\;+\;\underbrace{\varepsilon_T(\hat p)}_{\le\,DG/\sqrt{T}} ,""",
r"""\;+\;\underbrace{\varepsilon_T(\hat p)}_{\text{optimization residual}} ,""", "A16a")
rep(r"""\begin{proof}
Theorem~\ref{thm:rate} applied to $F_{\hat p}$ bounds the optimization term;
the floor term is $F_p$ evaluated at the two limits and is exact by definition.
The $\ell_1$ bound follows from $0\le f_i\le M$ as in
Proposition~\ref{prop:surrogate}.
\end{proof}""",
r"""\begin{proof}
The floor term is $F_p$ evaluated at the two limits and is exact by definition.
Theorem~\ref{thm:rate} applied to $F_{\hat p}$ bounds
$\E F_{\hat p}(\bar\theta_T)-F_{\hat p}(\theta^\dagger)$ by $DG/\sqrt{T}$;
$\varepsilon_T$ additionally carries the $p$-versus-$\hat p$ mismatch along
the trajectory, which vanishes as $\bar\theta_T$ approaches $\theta^\dagger$.
The $\ell_1$ bound follows from $0\le f_i\le M$ as in
Proposition~\ref{prop:surrogate}.
\end{proof}""", "A16b")
rep(r"""not diverge: it converges to the $I$-projection, the coupling whose reachable
row marginal $\hat p$ minimizes $\KL(\cdot\,\|\,p)$ over the polytope
$\{T\ge 0:\ \mathbf{1}^\top T=q,\ \mathrm{supp}(T)\subseteq E\}$
\cite{csiszar1975,peyre2019}.""",
r"""not diverge: its iterates accumulate at the coupling whose reachable row
marginal $\hat p$ is the KL-closest to $p$ over the polytope
$\{T\ge 0:\ \mathbf{1}^\top T=q,\ \mathrm{supp}(T)\subseteq E\}$
\cite{csiszar1975,gietl2013ipfp,peyre2019}.""", "A15")
rep(r"""expectations and apply Lemma~\ref{lem:unbiased} to $\|g_i\|^2$.""",
r"""expectations and use the row-marginal identity of Lemma~\ref{lem:unbiased}.""", "A13")
rep(r"""\bibitem{csiszar1975}""",
r"""\bibitem{gietl2013ipfp}
C.~Gietl and F.~P. Reffel, ``Accumulation points of the iterative proportional
fitting procedure,'' \emph{Statistics}, vol.~47, no.~6, pp. 1321--1335, 2013.

\bibitem{csiszar1975}""", "A15bib")

# ---- Section 5: Instances (I1, I5, I6, A11)
rep(r"""\emph{Adult} income classification \cite{uci_adult} with a uniform importance
target over the five race groups, and \emph{IMDb-Wiki} age regression
\cite{rothe2018imdbwiki} with a skewed importance target over age tiers. Both
are posed over $m=100$ critical groups with $K=3$ observed per step, $4000$
steps, $5$ seeds, tail-500 statistics.""",
r"""\emph{Adult} income classification \cite{uci_adult} (logistic regression,
$\eta{=}0.1$) with a uniform importance target over the five race groups, $100$
race-homogeneous groups of $30$ samples split $85/10/3/1/1$ by prevalence, and
\emph{IMDb-Wiki} age regression \cite{rothe2018imdbwiki} (linear regression on
$128$-d ResNet face embeddings, $\eta{=}10^{-2}$) over $100$ identities with a
cubically skewed importance target. Both use $K=3$ observed groups per step,
$H{=}5$ local steps per observed group before the weighted average (the
standard deviation from the one-step analysis, applied to every rule alike),
$4000$ steps, $5$ seeds, tail-500 statistics.""", "I1/I5/I6/A11")

# ---- Table 1 (T1a, T1e)
rep(r"""sees every group every step. The fixed multiplier $m/K$ diverges whenever
observation rates are non-uniform.}""",
r"""sees every group every step. The fixed multiplier $m/K$ diverges whenever
observation rates are non-uniform and is far off when they are uniform.}""", "T1e")
rep(r"""Adult, prevalence ($\nu{=}.60$) & $\best{0.2269}$ & $0.2479$ & div. & $0.2073$ \\""",
r"""Adult, prevalence ($\nu{=}.60$) & $\best{0.2269}$ & $0.2479$ & $0.670$ & $0.2073$ \\""", "T1a")

# ---- E1 (E1b)
rep(r"""difference. The fixed multiplier diverges on every instance, confirming that
naive rescaling is not an alternative to solving \eqref{eq:mot}.""",
r"""difference. The fixed multiplier diverges on both aligned instances and is far
off on the other two, so naive rescaling is no alternative to solving \eqref{eq:mot}.""", "E1b")

# ---- Table 2 caption: state the t convention (CHOICE)
rep(r"""advantage of transport. The excess residual transport pays averages $1.9$, and
the sign flips exactly where $\Delta_{\mathrm{floor}}$ crosses it. The five
Adult skews all sit above their crossover and are omitted.}""",
r"""advantage of transport, $t$ its Welch statistic over $5$ seeds (population
std). The excess residual transport pays averages $1.9$, and the sign flips
exactly where $\Delta_{\mathrm{floor}}$ crosses it. The five Adult skews all
sit above their crossover and are omitted.}""", "T2cap")

# ---- E2 (E2d) with compensating trims
rep(r"""evidence. On Adult, whose five skews are omitted from the table, the measured gain tracks
$\Delta_{\mathrm{floor}}$ almost exactly, within $4\%$ at three of five
($.0134$ against $.0129$, $.0050$ against $.0049$, $.0002$ against $.0003$):
the alignment floor is not merely an upper bound but a prediction. On IMDb-Wiki the gain is""",
r"""evidence. On Adult, whose five skews are omitted from the table, the measured gain tracks
$\Delta_{\mathrm{floor}}$ within $4\%$ at three of five
($.0134$ against $.0129$, $.0050$ against $.0049$, $.0002$ against $.0003$)
and exceeds it at the two most infeasible ($.0210$ against $.0110$, $.0181$
against $.0144$), where group-blind averaging sits further above its own
floor. On IMDb-Wiki the gain is""", "E2d")
rep(r"""This is the content of Theorem~\ref{thm:infeasible} read at finite $T$, and it
converts the sign of the comparison from an empirical surprise into a quantity
one computes in advance.""",
r"""This is Theorem~\ref{thm:infeasible} read at finite $T$: the sign of the
comparison is a quantity one computes in advance.""", "E2trim")
rep(r"""the criterion; the exact floors, which order the same eleven instances
correctly once the residual is accounted for, can. We report this because the
weaker bound is the one a reader would reach for first.""",
r"""the criterion; the exact floors can.""", "E3trim")

# ---- E5 threshold step (A10)
rep(r"""Sweeping $(\alpha,\gamma)$ on a $10\times10$ grid, the overall objective is""",
r"""Sweeping $(\alpha,\gamma)$ on a $10\times10$ grid (threshold step $\eta/20$), the overall objective is""", "A10")

# ---- Fig 2 -> vector
rep(r"""\includegraphics[width=0.99\columnwidth]{figs/severity_imdb.png}""",
r"""\includegraphics[width=0.99\columnwidth]{figs/severity_imdb.pdf}""", "F1")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print(n, "edits applied")
