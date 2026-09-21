"""One-shot (2026-09-21): fold the imbalance baselines (upsample, downsample, LDS) and the
stepsize-schedule sentence into both versions of Sec. 5, the appendix, and the two bibliographies.
Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:70], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

OLD_TAB = r"""\begin{tabular}{lcccc}
\toprule
Instance & \avot{} & unif.\ avg & $m/K$ & full \\
\midrule
Adult, prevalence ($\nu{=}.60$) & $\best{0.2269}$ & $0.2479$ & $0.670$ & $0.2073$ \\
Adult, aligned ($\nu{=}0$)      & $0.2075$ & $0.2077$ & div. & $0.2073$ \\
IMDb, skewed ($\nu{=}.31$)      & $\best{86.06}$ & $91.63$ & $8504$ & $82.95$ \\
IMDb, aligned ($\nu{=}0$)       & $\best{84.28}$ & $86.37$ & div. & $82.95$ \\
\bottomrule
\end{tabular}"""
NEW_TAB = r"""\begin{tabular}{lcccccc}
\toprule
Instance & \avot{} & unif.\ avg & upsamp. & LDS & $m/K$ & full \\
\midrule
Adult, prev.\ ($\nu{=}.60$) & $\best{0.2269}$ & $0.2479$ & $0.2288$ & -- & $0.670$ & $0.2073$ \\
Adult, aligned ($\nu{=}0$)  & $0.2075$ & $0.2077$ & $0.2075$ & -- & div. & $0.2073$ \\
IMDb, skewed ($\nu{=}.31$)  & $\best{86.06}$ & $91.63$ & $86.74$ & $94.28$ & $8504$ & $82.95$ \\
IMDb, aligned ($\nu{=}0$)   & $\best{84.28}$ & $86.37$ & $84.40$ & $89.43$ & div. & $82.95$ \\
\bottomrule
\end{tabular}"""
OLD_CAP = r"""\caption{Headline cells, tail-500 over $5$ seeds, decaying stepsize. \emph{full}
sees every group every step. The fixed multiplier $m/K$ diverges whenever
observation rates are non-uniform.}"""
NEW_CAP = r"""\caption{Headline cells, tail-500 over $5$ seeds, decaying stepsize. \emph{full}
sees every group every step; \emph{upsamp.}, self-normalized upsampling
(weights $\propto p_i/r_i$ within the batch); LDS, label-distribution
smoothing \cite{yang2021dir}, regression only. The fixed multiplier $m/K$
diverges whenever observation rates are non-uniform.}"""
OLD_E1_S = r"""The fixed
multiplier diverges on both aligned instances and is far off on the other
two: naive rescaling is no alternative to solving \eqref{eq:mot}."""
NEW_E1_S = r"""The fixed
multiplier diverges on both aligned instances and is far off on the other
two: naive rescaling is no alternative to solving \eqref{eq:mot}.
Self-normalized upsampling, the reweighting form of oversampling rare
groups, recovers most of the gain and transport the rest: $0.2288$
($t{=}5.8$ against transport) and $86.74$ ($t{=}2.6$). Downsampling
($\min(p_i/r_i,1)$, normalized) is never better than upsampling, and
label-distribution smoothing \cite{yang2021dir}, which reweights by label
rarity rather than by group observation, trails even group-blind averaging.
On the least represented group the margin over upsampling widens: $77.0$
against $80.0$ and $73.6$ against $75.6$ on IMDb-Wiki."""
OLD_E1_F = r"""The fixed multiplier diverges on both aligned instances and is far
off on the other two, so naive rescaling is no alternative to solving \eqref{eq:mot}."""
NEW_E1_F = r"""The fixed multiplier diverges on both aligned instances and is far
off on the other two, so naive rescaling is no alternative to solving \eqref{eq:mot}.
Two imbalance baselines sit between the two. Self-normalized upsampling
(weights $\propto p_i/r_i$, renormalized within the batch), the reweighting
form of oversampling rare groups, recovers most of the gain and transport
the rest: $0.2288$ against $0.2269$ on Adult prevalence ($t{=}5.8$) and
$86.74$ against $86.06$ on IMDb skewed ($t{=}2.6$, at the margin of
significance with $5$ seeds); on the aligned instances the two coincide, as
every convex rule must. Downsampling ($\min(p_i/r_i,1)$, normalized) is never
better than upsampling ($0.2308$, $86.90$). Label-distribution smoothing
\cite{yang2021dir}, the standard imbalanced-regression correction, reweights
by the rarity of the label value rather than by how rarely a group is
observed, and trails even group-blind averaging on both IMDb-Wiki instances
($94.28$, $89.43$). On the least represented group the margin of transport
over upsampling widens: $77.0$ against $80.0$ at $\nu{=}.31$ and $73.6$
against $75.6$ when aligned on IMDb-Wiki, $.073$ against $.075$ on Adult
prevalence. Upsampling is the one-shot heuristic for the marginal problem
\eqref{eq:mot} solves exactly, without the feasibility certificate or the
floor decomposition."""
OLD_PROTO_S = r"""Stepsize $\eta_t=\eta/(1+t/1000)$
unless stated, $4000$ steps, $5$ seeds, $F_p$ over the last $500$ steps,
mean $\pm$ std."""
NEW_PROTO_S = r"""Stepsize $\eta_t=\eta/(1+t/1000)$
unless stated, fixed before the comparison and shared by every rule (a
faster decay widens the IMDb-Wiki gap, a constant stepsize narrows it, the
winner never changes; extended version), $4000$ steps, $5$ seeds, $F_p$ over
the last $500$ steps, mean $\pm$ std."""
OLD_PROTO_F = r"""Stepsize
$\eta_t=\eta/(1+t/1000)$ unless stated, $4000$ steps, $5$ seeds; we report
$F_p$ averaged over the last $500$ steps, mean $\pm$ std over seeds."""
NEW_PROTO_F = r"""Stepsize
$\eta_t=\eta/(1+t/1000)$ unless stated, fixed before the comparison and
shared by every rule; across nine schedules (constant, hyperbolic with
$T_0\in\{250,\dots,16000\}$, inverse square root, step, cosine) the winner
never changes on any instance, only the margin does: a faster decay puts
full coverage on its floor and widens the IMDb-Wiki gap (cosine: $84.12$
against $90.69$), a constant stepsize narrows it to a tie. $4000$ steps, $5$
seeds; we report $F_p$ averaged over the last $500$ steps, mean $\pm$ std
over seeds."""
OLD_APP = r"""$\argmin F_w$ is closed-form for least squares and Newton to
machine precision for the logistic loss."""
NEW_APP = r"""$\argmin F_w$ is closed-form for least squares and Newton to
machine precision for the logistic loss. Baselines of Table~\ref{tab:overall}:
upsampling weights the observed groups $\propto p_i/r_i$, downsampling
$\propto\min(p_i/r_i,1)$, both renormalized within the batch; LDS
\cite{yang2021dir} weights each sample by the inverse of the Gaussian-smoothed
age histogram (unit bins, kernel $5$, $\sigma{=}2$, mean weight $1$),
averaged within each group and renormalized within the batch."""
BIB_OLD = r"""\bibitem{rothe2018imdbwiki}"""
BIB_NEW = r"""\bibitem{yang2021dir}
Y.~Yang, K.~Zha, Y.-C. Chen, H.~Wang, and D.~Katabi, ``Delving into deep
imbalanced regression,'' in \emph{Proc. Int. Conf. Machine Learning (ICML)},
2021.

\bibitem{rothe2018imdbwiki}"""

if __name__ == "__main__":
    for f in ("sections/experiments_short.tex", "sections/experiments_full.tex"):
        sub(f, OLD_TAB, NEW_TAB)
        sub(f, OLD_CAP, NEW_CAP)
    sub("sections/experiments_short.tex", OLD_E1_S, NEW_E1_S)
    sub("sections/experiments_full.tex", OLD_E1_F, NEW_E1_F)
    sub("sections/experiments_short.tex", OLD_PROTO_S, NEW_PROTO_S)
    sub("sections/experiments_full.tex", OLD_PROTO_F, NEW_PROTO_F)
    sub("appendix.tex", OLD_APP, NEW_APP)
    for f in ("main_fit.tex", "main_full.tex"):
        sub(f, BIB_OLD, BIB_NEW)
    print("edits ok")
