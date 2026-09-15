import io, re, sys
SRC = r"C:\Users\vihaa\fedavot-overleaf\complete.tex"
DST = r"C:\Users\vihaa\fedavot-overleaf\complete_short.tex"
L = io.open(SRC, encoding="utf-8").read().split("\n")
def R(a, b): return L[a-1:b]          # 1-indexed inclusive
NL = chr(10)

out = []
out += R(1, 35)                        # preamble (verbatim)
out += [r"\renewcommand{\topfraction}{0.95}\renewcommand{\textfraction}{0.03}\setcounter{topnumber}{3}\setcounter{totalnumber}{4}"]
abstract = R(36, 43)
abstract = [x.replace(" Naive fixes, such as fixed reweighting or oversampling, either ignore which groups a given batch can actually show or inflate variance and discard data.", "") for x in abstract]
out += abstract                        # title + abstract (one sentence dropped)
intro = R(45, 51)                      # introduction (verbatim minus the 4th paragraph and two sentences)
intro = [x.replace(" Existing remedies do not resolve this: importance-sampling and variance-reduction methods for SGD assume itemwise access rather than subset-masked batches, distributionally robust and fairness-reweighting methods operate on the objective rather than on the batch-level aggregation constraint, and methods that correct for a known per-group observation rate assume a fixed correction factor rather than one that adapts to which combinations of groups can jointly appear.", "")
         .replace(" We summarize our contributions below.", "") for x in intro]
out += intro
# related work dropped entirely
out += R(76, 77) + R(84, 84)           # section 2 intro + critical-groups definition
out += [""] + R(93, 97)                # target measure + fair objective
out += [""] + R(99, 99)                # SGD / subset patterns
out += R(105, 122)                     # weighted aggregation, constraints, MOT
out += R(136, 143)                     # feasibility theorem
out += [""] + R(151, 151)              # IPFP sentence
sec3 = R(182, 189)                     # section 3 intro + "Sampling and weighting" heading
l190 = L[189]; sec3 += [l190[:l190.index(" Define $T[i,j]=q_j Y[i,j]$")] + "."]   # restated marginal constraints dropped
sec3 += R(195, 208)                    # estimator, assumption
out += [x.replace(r"\eqref{eq:marginals}", r"\eqref{eq:constraints}") for x in sec3]
out += [x.replace(r"\eqref{eq:marginals}", r"\eqref{eq:constraints}") for x in R(211, 216)]   # lemma statement
out += [r"\begin{proof}", r"Condition on $\theta_t$, take expectation over $j_t\sim q$, and use $\sum_j q_j Y[i,j]=\mu_i$ from \eqref{eq:constraints}.", r"\end{proof}"]
out += R(246, 262)                     # main theorem (algorithm box dropped; update is stated in the text)
out += [r"\begin{proof}[Proof sketch]",
        r"Non-expansiveness of $\Pi_{\mathcal{C}}$ gives $\|\theta_{t+1}-\theta^\star\|^2 \le \|\theta_t-\theta^\star\|^2 - 2\eta_t \langle g_t, \theta_t-\theta^\star\rangle + \eta_t^2 \|g_t\|^2$; taking conditional expectation, applying Lemma~\ref{lem:unbiased}, convexity and Assumption~\ref{assump:gradient_bound}, telescoping over $t$, and using Jensen's inequality on $\bar{\theta}_T$ gives \eqref{eq:key-bound}; the constant step $\eta=D/(G\sqrt{T})$ gives \eqref{eq:rate}. The same rate holds for $\eta_t=\eta_0/\sqrt{t}$ up to constants.",
        r"\end{proof}"]
out += [x.replace(r"width=0.88\textwidth", r"width=0.56\textwidth") for x in R(421, 435)]   # adult figure*, placed early so it floats to the top of page 4
out += R(309, 314)                     # infeasible masks intro
out += R(323, 335) + R(351, 358)       # entropic projection + final bias bound
proto = NL.join(R(390, 394))           # experiments: protocol + IMDb
proto = re.sub(r" Theorem~\\ref\{thm:main\} analyzes a single weighted gradient step per iteration;.*?since every rule consumes the same local updates\.", "", proto)
proto = re.sub(r" Recall that instantiating the feasibility condition.*?hold as well\.", "", proto, flags=re.S)
out += proto.split(NL)
out += R(396, 397)                     # adult setup
imdbfig = NL.join(R(398, 409)).replace(r"width=\linewidth", r"width=0.54\linewidth").replace("; the" + NL + "  fixed-multiplier correction is unstable and off scale.}", ".}")
out += imdbfig.split(NL)               # IMDb infeasible figure
out += R(502, 523)                     # sweep table, placed before the prose so it floats to page 4
prose = NL.join(R(459, 501)).replace(r"(Figs.~\ref{fig:imdb-infeasible} and~\ref{fig:imdb-feasible})", r"(Fig.~\ref{fig:imdb-infeasible})")
a = prose.index("The" + NL + "fixed-multiplier correction is unstable here"); b = prose.index("In the aligned regime the same")
prose = prose[:a] + prose[b:]          # my fixed-multiplier aside dropped
c = prose.index("The step-size schedule is"); prose = prose[:c].rstrip()   # my step-size explanation dropped
out += prose.split(NL)
adult = NL.join(R(538, 562))           # adult results (CVaR paragraph dropped)
i = adult.index("Along the"); j = adult.index("In the aligned regime")
adult = adult[:i] + adult[j:]
k = adult.index("Equal observability for every"); adult = adult[:k].rstrip()   # closing sentence dropped
adult = adult.replace(", with the" + NL + "uniform average worse still at $0.189$ and $0.119$)", ")")   # my clause dropped
out += adult.split(NL)
tail = NL.join(L[565:])                # bias-validation paragraph dropped; keep bibliography lines
out += tail[tail.index(r"\bibliographystyle"):].split(NL)
s = NL.join(out)
for ref in sorted(set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", s))):
    if ("\\label{%s}" % ref) not in s: print("DANGLING REF:", ref)
io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print(len(out), "lines written")
