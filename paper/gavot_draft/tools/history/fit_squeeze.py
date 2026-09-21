"""One-shot (2026-09-21, after herlock_trims.py): compress Sec. 5 short prose and captions so the
fit build reaches 4 pages. Every detail removed here is still in sections/experiments_full.tex
(the extended version) and is listed in review/CUT_LEDGER.md. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
S = "sections/experiments_short.tex"

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

PROTO_OLD = r"""\emph{Adult} income classification \cite{uci_adult}: logistic regression
($\eta{=}0.1$) on $100$ race-homogeneous groups of $30$ samples, groups per
race proportional to prevalence ($85/10/3/1/1$), target uniform over the
five races, so a group from the smallest race carries $p_i=0.2$.
\emph{IMDb-Wiki} age regression \cite{rothe2018imdbwiki}: linear regression
on $128$-d face embeddings ($\eta{=}10^{-2}$) over $100$ identities with the
cubic target $p_i\propto(101-i)^3$. Observation rates are swept: on Adult
$r\propto p^{\beta}$, $\beta\in\{0,\tfrac14,\tfrac12,\tfrac34,1\}$, from
uniform observation (prevalence, $\nu{=}.60$) to aligned ($\nu{=}0$); on
IMDb-Wiki $r_i\propto i^{\beta}$, $\beta\in\{0,\tfrac12,1,\tfrac32,2,3\}$,
from uniform ($\nu{=}.31$) to the mirror image of $p$ ($\nu{=}.88$), plus
the aligned $r_i\propto 101-i$ ($\nu{=}0$): eleven instances. Each step
observes $K{=}3$ groups drawn $\propto r$; the plan is fitted once per
instance by Sinkhorn scaling on the mask. Each observed group takes $H{=}5$
local steps before the weighted average, the standard practical deviation
from the one-step analysis, applied to every rule alike: \avot{};
\emph{group-blind averaging}, the uniform average over the observed groups
($\tilde p_i=r_i/K$); the \emph{fixed multiplier} $m/K$; and \emph{full},
every group every step weighted by $p$. Stepsize $\eta_t=\eta/(1+t/1000)$
unless stated, fixed before the comparison and shared by every rule (faster
decays widen the IMDb-Wiki gap, never flip a winner; extended version),
$4000$ steps, $5$ seeds, $F_p$ over the last $500$ steps, mean $\pm$ std. The floors of Theorem~\ref{thm:infeasible} are exact
(closed form for least squares, Newton for the logistic loss). Full protocol
and the closed-form check of the mirrored instance are in the appendix; the
extended version carries the unabridged discussion."""
PROTO_NEW = r"""\emph{Adult} income classification \cite{uci_adult}: logistic regression
($\eta{=}0.1$) on $100$ race-homogeneous groups of $30$ samples, groups per
race $\propto$ prevalence ($85/10/3/1/1$), target uniform over the five
races ($p_i=0.2$ for a smallest-race group). \emph{IMDb-Wiki} age
regression \cite{rothe2018imdbwiki}: linear regression on $128$-d face
embeddings ($\eta{=}10^{-2}$) over $100$ identities, cubic target
$p_i\propto(101-i)^3$. Observation rates are swept: Adult $r\propto
p^{\beta}$, $\beta\in\{0,\tfrac14,\tfrac12,\tfrac34,1\}$, from prevalence
($\nu{=}.60$) to aligned ($\nu{=}0$); IMDb-Wiki $r_i\propto i^{\beta}$,
$\beta\in\{0,\tfrac12,1,\tfrac32,2,3\}$, from uniform ($\nu{=}.31$) to the
mirror image of $p$ ($\nu{=}.88$), plus aligned $r_i\propto 101-i$
($\nu{=}0$): eleven instances. Each step observes $K{=}3$ groups drawn
$\propto r$, each taking $H{=}5$ local steps before the weighted average,
for every rule alike: \avot{}; \emph{group-blind averaging}, uniform over
the observed groups ($\tilde p_i=r_i/K$); the \emph{fixed multiplier}
$m/K$; \emph{full}, every group every step weighted by $p$. Stepsize
$\eta_t=\eta/(1+t/1000)$, fixed before the comparison and shared by every
rule (faster decays widen the IMDb-Wiki gap, never flip a winner), $4000$
steps, $5$ seeds, $F_p$ over the last $500$ steps. Floors are exact
(appendix, with the full protocol and the closed-form check); the extended
version carries the unabridged discussion."""

FIG2_OLD = r"""\includegraphics[width=0.92\columnwidth]{figs/severity_imdb.pdf}
\caption{IMDb-Wiki severity sweep. Solid, measured tail-500 ($\pm1$ std);
dashed, the exact floor $\Phi(\cdot)$ each rule converges to. Left, constant
stepsize: the optimization residual swamps the alignment gain and transport
loses everywhere, even where the floors are seven units apart. Right, decaying
stepsize: the residual collapses and the measured curves track their floors, so
transport wins until the floors close at high $\nu$. The sign is set by which of
the two terms of \eqref{eq:infeasible} dominates, not by the regime label.}"""
FIG2_NEW = r"""\includegraphics[width=0.88\columnwidth]{figs/severity_imdb.pdf}
\caption{IMDb-Wiki severity sweep: measured tail-500 (solid, $\pm1$ std)
against the exact floor $\Phi(\cdot)$ of each rule (dashed). Left, constant
stepsize: the residual swamps the alignment gain and transport loses
everywhere. Right, decaying: the curves track their floors and transport wins
until the floors close at high $\nu$; the sign is set by \eqref{eq:infeasible}.}"""

RARE_OLD = r"""\includegraphics[width=0.99\columnwidth]{figs/rare_group_fit.pdf}
\caption{Loss on the least represented group, decaying stepsize. Left,
Adult: cross-entropy on race Other ($1$ group of $30$, $p_i=0.2$) against
the observation-rate exponent. Right, IMDb-Wiki: MSE on the $20$
highest-importance identities, the least observed once $\beta>0$. Same runs
as Table~\ref{tab:overall}; constant-stepsize panels in the extended version.}"""
RARE_NEW = r"""\includegraphics[width=0.95\columnwidth]{figs/rare_group_fit.pdf}
\caption{Loss on the least represented group, decaying stepsize: Adult,
cross-entropy on race Other ($p_i=0.2$) against the observation exponent;
IMDb-Wiki, MSE on the $20$ top-importance identities, the least observed
once $\beta>0$. Same runs as Table~\ref{tab:overall}.}"""

E1_OLD = r"""Table~\ref{tab:overall} reports the four instances a practitioner would
recognize. Transport wins on three: Adult under prevalence-proportional
availability, $0.2269$ against $0.2479$ ($t{=}45$), and both IMDb cells,
$86.06$ against $91.63$ ($t{=}21$) and $84.28$ against $86.37$ ($t{=}13$). On
Adult with aligned availability the two coincide at the oracle value, as
Proposition~\ref{prop:surrogate} predicts when $\tilde p=p$. The fixed
multiplier diverges on both aligned instances and is far off on the other
two: naive rescaling is no alternative to solving \eqref{eq:mot}.
Self-normalized upsampling, the reweighting form of oversampling rare
groups, recovers most of the gain and transport the rest ($t{=}5.8$ and
$2.6$ against it); downsampling never beats it, and LDS, which reweights by
label rarity rather than by group observation, trails even group-blind
averaging. On the least represented group the margin over upsampling widens
($77.0$ against $80.0$, $73.6$ against $75.6$ on IMDb-Wiki)."""
E1_NEW = r"""Table~\ref{tab:overall} reports the four instances a practitioner would
recognize. Transport wins on three: Adult under prevalence availability,
$0.2269$ against $0.2479$ ($t{=}45$), and both IMDb cells, $86.06$ against
$91.63$ ($t{=}21$) and $84.28$ against $86.37$ ($t{=}13$); on Adult aligned
the two coincide at the oracle value, as Proposition~\ref{prop:surrogate}
predicts when $\tilde p=p$. The fixed multiplier diverges on both aligned
instances and is far off on the other two. Self-normalized upsampling, the
reweighting form of oversampling rare groups, recovers most of the gain and
transport the rest ($t{=}5.8$, $2.6$ against it); downsampling never beats
it, and LDS, which reweights by label rarity rather than group observation,
trails even group-blind averaging. On the least represented group the
margin over upsampling widens ($77.0$ against $80.0$, $73.6$ against $75.6$
on IMDb-Wiki)."""

E2_OLD = r"""Fig.~\ref{fig:rare} reads the same runs on the group the target exists for.
On Adult, transport lowers the loss on race Other at every skew and under
both stepsizes: $.073$ against $.119$ on the prevalence instance (full
$.031$), $.031$ against $.035$ when aligned, matching full; Amer-Indian
behaves the same way. On IMDb-Wiki the top-importance identities show the
crossover of Table~\ref{tab:severity} one step earlier: under decay
transport wins at $\nu\le.70$ ($77.0$ against $86.4$ at $\nu{=}.31$, full
$72.2$; $73.6$ against $79.9$ aligned) and loses at the three most
infeasible skews. The single most starved group (largest $p_i/r_i$) is Other
itself on Adult ($p_i/r_i{=}6.7$) and the top identity on IMDb-Wiki: $253$
against $331$ at $\nu{=}.31$, $373$ against $380$ at $\nu{=}.59$ (full
$219$), a $30$-image group so $\pm5$ to $10$ across seeds. The rare-group
loss tells the same story as the objective, more sensitively."""
E2_NEW = r"""Fig.~\ref{fig:rare} reads the same runs on the group the target exists for.
On Adult, transport lowers the loss on race Other at every skew: $.073$
against $.119$ on the prevalence instance (full $.031$), $.031$ against
$.035$ aligned, matching full; Amer-Indian behaves the same way. On
IMDb-Wiki the top-importance identities show the crossover of
Table~\ref{tab:severity} one step earlier: transport wins at $\nu\le.70$
($77.0$ against $86.4$ at $\nu{=}.31$, full $72.2$; $73.6$ against $79.9$
aligned) and loses at the three most infeasible skews. The single most
starved group (largest $p_i/r_i$) is Other itself on Adult and the top
identity on IMDb-Wiki, $253$ against $331$ at $\nu{=}.31$ (full $219$; a
$30$-image group, $\pm5$ to $10$ across seeds). The rare-group loss tells
the same story as the objective, more sensitively."""

E4_OLD = r"""At constant stepsize (Fig.~\ref{fig:severity}, left) transport loses on all
six IMDb skews, by up to $7.9$, even where the floors are $6.99$ apart. A
starved group has $p_i>r_i$, so the plan delivers at most $r_i$ of its mass:
$\hat p$ truncates at the observation rate and, as $\nu$ grows, $\hat p$ and
$\tilde p$ starve the same groups, so the floors converge
($\Delta_{\mathrm{floor}}$ from $6.99$ to $0.02$; both $105.9$ at
$\nu{=}.88$, appendix). What transport still does is concentrate weight on
the starved group whenever it appears, $p_i/r_i$ times its batch share:
Lemma~\ref{lem:variance} bounds the second moment identically for both
rules, but the variance about the mean is larger, largest on the rare
group, and at constant stepsize the iterates sit on a noise floor
proportional to it. Under $\eta_t=\eta/(1+t/1000)$ that floor decays, the
curves fall onto their dashed floors, and what remains is the residual,
$2.3$ at $\nu{=}.88$, the one significant loss. Transport helps exactly
while there is mass left to move."""
E4_NEW = r"""At constant stepsize (Fig.~\ref{fig:severity}, left) transport loses on all
six IMDb skews, by up to $7.9$, even where the floors are $6.99$ apart. A
starved group has $p_i>r_i$, so $\hat p$ truncates at the observation rate;
as $\nu$ grows $\hat p$ and $\tilde p$ starve the same groups and the floors
converge ($\Delta_{\mathrm{floor}}$ from $6.99$ to $0.02$, both $105.9$ at
$\nu{=}.88$, appendix). Transport still concentrates weight on a starved
group whenever it appears, $p_i/r_i$ times its batch share:
Lemma~\ref{lem:variance} bounds the second moment identically for both
rules, but the variance about the mean is larger, and at constant stepsize
the iterates sit on a noise floor proportional to it. Under
$\eta_t=\eta/(1+t/1000)$ that floor decays, the curves fall onto their
dashed floors, and what remains is the residual, $2.3$ at $\nu{=}.88$, the
one significant loss. Transport helps exactly while there is mass left to move."""

E5_OLD = r"""On a $10\times10$ $(\alpha,\gamma)$ grid the overall objective is minimized
on the $\gamma=1$ edge of every instance, $\kappa(1,\gamma)=1$ made visible:
risk aversion costs the average. It earns its keep once, on the worst race of
Adult under prevalence availability: \avotcvar{} at $(0.2,0.7)$ reaches
$0.3624$ against $0.3679$ for \avot{} and $0.3994$ for group-blind
averaging. Per race, transport improves four of five (Black $.179$ vs
$.200$, Asian-Pac $.368$ vs $.399$, Am-Ind $.175$ vs $.189$, Other $.073$
vs $.119$) and regresses only the majority ($.339$ vs $.332$). On the least
represented group the layer never helps: the grid's best rare-group loss is
at $\gamma{=}1$ on all four headline instances, and $(0.1,0.1)$ nearly
triples the loss on Other ($.207$ against $.073$) and lifts the IMDb-Wiki
top identities from $77.0$ to $103$. CVaR tilts among the groups present in
the batch, and the rare group is absent from most, so the tilt lands
elsewhere; on top of transport it multiplies weights already $p_i/r_i$ large
and amplifies variance, not alignment. Risk aversion changes the functional,
not who is observed."""
E5_NEW = r"""On a $10\times10$ $(\alpha,\gamma)$ grid the overall objective is minimized
on the $\gamma=1$ edge of every instance, $\kappa(1,\gamma)=1$ made visible:
risk aversion costs the average. It earns its keep once, on the worst race of
Adult under prevalence availability: \avotcvar{} at $(0.2,0.7)$ reaches
$0.3624$ against $0.3679$ for \avot{} and $0.3994$ for group-blind averaging
(per-race table in the appendix: transport improves four races of five and
regresses only the majority). On the least represented group the layer never
helps: the grid's best rare-group loss is at $\gamma{=}1$ on all four
headline instances, and $(0.1,0.1)$ nearly triples the loss on Other
($.207$ against $.073$) and lifts the IMDb-Wiki top identities from $77.0$
to $103$. CVaR tilts among the groups present in the batch, and the rare
group is absent from most; on top of transport it multiplies weights already
$p_i/r_i$ large and amplifies variance, not alignment. Risk aversion changes
the functional, not who is observed."""

APPD_OLD = r"""Transport improves four of five categories and regresses only the majority group,
the expected effect of reweighting toward a category-uniform target; the residual
loss on the two smallest categories is the unreachable mass of Cor.~\ref{cor:batchsize}."""
APPD_NEW = r"""Four of five categories improve and only the majority regresses, the expected
effect of a category-uniform target; the residual on the two smallest is the
unreachable mass of Cor.~\ref{cor:batchsize}."""

if __name__ == "__main__":
    for old, new in ((PROTO_OLD, PROTO_NEW), (FIG2_OLD, FIG2_NEW), (RARE_OLD, RARE_NEW),
                     (E1_OLD, E1_NEW), (E2_OLD, E2_NEW), (E4_OLD, E4_NEW), (E5_OLD, E5_NEW)):
        sub(S, old, new)
    sub("appendix.tex", APPD_OLD, APPD_NEW)
    print("ok")
