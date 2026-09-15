import io, re, sys
SRC = r"C:\Users\vihaa\fedavot-overleaf\complete.tex"
DST = r"C:\Users\vihaa\fedavot-overleaf\complete_short.tex"
L = io.open(SRC, encoding="utf-8").read().split("\n")
def R(a, b): return L[a-1:b]          # 1-indexed inclusive

out = []
out += R(1, 43)                        # preamble, title, abstract (verbatim)
intro = R(45, 51)                      # introduction (verbatim minus the 4th paragraph and two sentences)
intro = [x.replace(" Existing remedies do not resolve this: importance-sampling and variance-reduction methods for SGD assume itemwise access rather than subset-masked batches, distributionally robust and fairness-reweighting methods operate on the objective rather than on the batch-level aggregation constraint, and methods that correct for a known per-group observation rate assume a fixed correction factor rather than one that adapts to which combinations of groups can jointly appear.", "")
         .replace(" We summarize our contributions below.", "") for x in intro]
out += intro
pass                                   # related work dropped entirely
out += R(76, 77) + R(84, 84)           # section 2 intro + critical-groups definition
out += [""] + R(93, 97)                # target measure + fair objective
out += [""] + R(99, 99)                # SGD / subset patterns
l104 = L[103]; out += [l104[l104.index("Throughout"):]]
out += R(105, 122)                     # weighted aggregation, constraints, MOT
out += R(136, 143)                     # feasibility theorem
out += [""] + R(151, 151)              # IPFP sentence
out += [r"If $p$ and $q$ satisfy~\eqref{eq:feasibility}, IPFP converges to a feasible solution of~\eqref{eq:mot}~\cite{sinkhorn1967concerning, knight2008sinkhorn}."]
out += R(182, 208)                     # section 3 through assumption
out += R(211, 216)                     # lemma statement
out += [r"\begin{proof}", r"Condition on $\theta_t$, take expectation over $j_t\sim q$, and use $\sum_j q_j Y[i,j]=\mu_i$ from \eqref{eq:marginals}.", r"\end{proof}"]
out += R(246, 262)                     # main theorem (algorithm box dropped; update is stated in the text)
out += [r"\begin{proof}[Proof sketch]",
        r"Non-expansiveness of $\Pi_{\mathcal{C}}$ gives $\|\theta_{t+1}-\theta^\star\|^2 \le \|\theta_t-\theta^\star\|^2 - 2\eta_t \langle g_t, \theta_t-\theta^\star\rangle + \eta_t^2 \|g_t\|^2$; taking conditional expectation, applying Lemma~\ref{lem:unbiased}, convexity and Assumption~\ref{assump:gradient_bound}, telescoping over $t$, and using Jensen's inequality on $\bar{\theta}_T$ gives \eqref{eq:key-bound}; the constant step $\eta=D/(G\sqrt{T})$ gives \eqref{eq:rate}. The same rate holds for $\eta_t=\eta_0/\sqrt{t}$ up to constants.",
        r"\end{proof}"]
out += R(309, 314)                     # infeasible masks intro
out += R(323, 335) + R(351, 358)       # entropic projection + final bias bound (Interpretation and the surrogate-rate display dropped)
proto = R(390, 394)                    # experiments: protocol + IMDb
proto = [re.sub(r" Theorem~\\ref\{thm:main\} analyzes a single weighted gradient step per iteration;.*?since every rule consumes the same local updates\.", "", x) for x in proto]
out += proto
out += R(396, 397)                     # adult setup
out += [x.replace(r"width=\linewidth", r"width=0.68\linewidth") for x in R(398, 409)]   # IMDb infeasible figure
out += [x.replace(r"width=0.88\textwidth", r"width=0.86\linewidth").replace(r"\begin{figure*}[t]", r"\begin{figure}[t]").replace(r"\end{figure*}", r"\end{figure}") for x in R(421, 435)]   # adult figure, single column
prose = [x.replace(r"(Figs.~\ref{fig:imdb-infeasible} and~\ref{fig:imdb-feasible})", r"(Fig.~\ref{fig:imdb-infeasible})") for x in R(459, 523)]
out += prose
adult = "\n".join(R(538, 562))         # adult results (CVaR paragraph dropped)
i = adult.index("Along the"); j = adult.index("In the aligned regime")
adult = adult[:i] + adult[j:]
out += adult.split("\n")
tail = "\n".join(L[565:])              # bias-validation paragraph dropped; keep bibliography lines
out += tail[tail.index(r"\bibliographystyle"):].split("\n")
s = "\n".join(out)
for ref in sorted(set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", s))):
    if ("\\label{%s}" % ref) not in s: print("DANGLING REF:", ref)
io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print(len(out), "lines written")
