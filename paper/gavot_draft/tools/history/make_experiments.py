import io
D = r"C:\Users\vihaa\fedavot-convergence\paper\gavot_draft"
NL = chr(10)
main = io.open(D + r"\main.tex", encoding="utf-8").read().split(NL)
s = next(i for i, l in enumerate(main) if l.startswith(r"\section{Experiments}"))
e = next(i for i, l in enumerate(main) if l.startswith(r"\section{Conclusion}"))
sec5 = NL.join(main[s:e])

def rep(s, old, new):
    assert s.count(old) == 1, old[:70]
    return s.replace(old, new)

header = r"""% =====================================================================
%  Section 5: Experiments  (his verified Sec. 5 plus, from the previous
%  Overleaf: the common protocol, fuller instance descriptions, and the
%  closed-form validation of Theorem thm:infeasible.  Labels kept.)
% =====================================================================
"""

sec5 = rep(sec5,
r"""\noindent\textbf{Instances.}
\emph{Adult} income classification \cite{uci_adult} (logistic regression,
$\eta{=}0.1$) with a uniform importance target over the five race groups, $100$
race-homogeneous groups of $30$ samples split $85/10/3/1/1$ by prevalence, and
\emph{IMDb-Wiki} age regression \cite{rothe2018imdbwiki} (linear regression on
ResNet embeddings, $\eta{=}10^{-2}$) over $100$ identities with a cubically
skewed importance target. Both use $K=3$ observed groups per step,
$H{=}5$ local steps per observed group before the weighted average, $4000$
steps, $5$ seeds, tail-500 statistics. Availability rates $r$ are swept through
a family indexed by $\beta$, from prevalence-proportional to importance-aligned
on Adult and through increasing skew on IMDb-Wiki, giving eleven instances whose
infeasible mass $\nu$ of \eqref{eq:batchlaw} ranges from $0$ to $88\%$. On both
the perturbation frontier is closed-form, so the floors $\Phi(p),\Phi(\hat p),
\Phi(\tilde p)$ of Theorem~\ref{thm:infeasible} are exact rather than estimated.
Besides group-blind averaging we include the fixed multiplier $m/K$, the
rescaling that assumes a uniform observation rate.""",
r"""\noindent\textbf{Instances.}
\emph{Adult} income classification \cite{uci_adult}: logistic regression
($d{=}109$ with intercept, cross-entropy, $\eta{=}0.1$) on $100$
race-homogeneous groups of $30$ samples, the number of groups per race
proportional to its prevalence (White/Black/Asian-Pac./Amer-Ind./Other
$=85/10/3/1/1$); the importance target is the fairness target itself, $1/5$
per race divided equally among its groups, so a group from the smallest
race carries $p_i=0.2$. \emph{IMDb-Wiki} age regression
\cite{rothe2018imdbwiki}: linear regression of age on $128$-d ResNet face
embeddings ($\eta{=}10^{-2}$) over the first $100$ identities with $30$
images, with the cubic importance target $p_i\propto(101-i)^3$.
Observation rates are swept through a one-parameter family: on Adult
$r\propto p^{\beta}$, $\beta\in\{0,\tfrac14,\tfrac12,\tfrac34,1\}$, from
uniform observation (prevalence regime, $\nu{=}.60$: the five groups of the
three smallest races hold $60\%$ of the target against $r_i\approx K/m$)
to importance-aligned ($\nu{=}0$); on IMDb-Wiki $r_i\propto i^{\beta}$,
$\beta\in\{0,\tfrac12,1,\tfrac32,2,3\}$, from uniform observation
($\nu{=}.31$, nine groups) to the mirror image of $p$ ($\nu{=}.88$, $41$
groups), plus the aligned $r_i\propto 101-i$ ($\nu{=}0$). Eleven instances,
$\nu$ from $0$ to $.88$.

\noindent\textbf{Protocol.}
Each step observes $K{=}3$ groups drawn without replacement with
probabilities $\propto r$, which induces $q$ over the $\binom{100}{3}$
compositions; $q$ is estimated from $10^6$ draws of the sampler and the plan
from \eqref{eq:ipfp} on the membership mask, once per instance. Each
observed group takes $H{=}5$ local steps on its own data before the weighted
average, the standard practical deviation from the one-step analysis,
applied to every rule alike since all rules consume the same local updates
from the same draw $A^t$. Rules: \avot{}; \emph{group-blind averaging}, the
uniform average over the observed groups (Proposition~\ref{prop:surrogate}
with $\tilde p_i=r_i/K$); the \emph{fixed multiplier} $m/K$, the rescaling
$(m/K)\,p_i$ that presumes uniform observation; and \emph{full}, every group
every step weighted by $p$, the reference $\Phi(p)$. Stepsize
$\eta_t=\eta/(1+t/1000)$ unless stated, $4000$ steps, $5$ seeds; we report
$F_p$ averaged over the last $500$ steps, mean $\pm$ std over seeds. On both
instances $\argmin F_w$ is available to machine precision (closed form for
least squares, Newton for the logistic loss), so the floors
$\Phi(p),\Phi(\hat p),\Phi(\tilde p)$ of Theorem~\ref{thm:infeasible} are
exact rather than estimated, and in every instance with $\nu=0$ the
iteration \eqref{eq:ipfp} converges to $10^{-8}$, certifying the remaining
inequalities of \eqref{eq:hall}.""")

sec5 = rep(sec5,
r"""decays, the measured curves fall onto their dashed floors, and every sign
reversal attributable to the stepsize disappears. The residual is a property of
the schedule, not of the estimator.""",
r"""decays, the measured curves fall onto their dashed floors, and every sign
reversal attributable to the stepsize disappears. The residual is a property of
the schedule, not of the estimator.

\noindent\textbf{E6: the decomposition in closed form.}
The mirrored IMDb-Wiki instance ($\nu{=}.88$) is where
Theorem~\ref{thm:infeasible} can be read off exactly. The Sinkhorn limit
truncates the target at the observation-rate ceiling,
$\hat p_i\approx\min(p_i,r_i)$ up to renormalization (maximum deviation
$.023$), with $\|p-\hat p\|_1=1.58$ of a possible $2$. The frontier is least
squares, so $\Phi(p)=82.9$, matching the measured full plateau $82.95$, and
$\Phi(\hat p)=105.9$: the alignment floor is $23.0$ and the realized bias
equals its exact expression $|(p-\hat p)^\top L(\theta^\dagger)|=30.7$, where
$L$ collects the per-group risks, while the $\ell_1$ form $2M\|p-\hat p\|_1$
is conservative since $M\ge\max_i L_i(\theta^\dagger)\approx 454$.
Group-blind averaging has the same floor to two decimals,
$\Phi(\tilde p)=105.9$: both surrogates starve the same groups, so
$\Delta_{\mathrm{floor}}$ vanishes and the entire measured gap between the
two rules at this endpoint of Table~\ref{tab:severity} is residual, which is
why it is the one instance where transport still loses under decay.""")

io.open(D + r"\experiments_full.tex", "w", encoding="utf-8", newline=NL).write(header + sec5 + NL)

s2 = next(i for i, l in enumerate(main) if l.startswith(r"\section{Group-Blind SGD"))
s4 = next(i for i, l in enumerate(main) if l.startswith(r"\section{A Risk-Averse Layer"))
c6 = next(i for i, l in enumerate(main) if l.startswith(r"\section{Conclusion}"))
full = (main[:s2-1] + [r"\input{problem_formulation}", r"\input{proposed_solution}", ""]
        + main[s4-1:s-1] + [r"\input{experiments_full}", ""] + main[c6-1:])
io.open(D + r"\main_full.tex", "w", encoding="utf-8", newline=NL).write(NL.join(full))
print("ok", s, e, s2, s4, c6)
