"""One-shot (2026-09-21): apply review/ICASSP_TEMPLATE_GRADE_2026-09-21.md (second grade, against the
rendered Template.pdf), no deletions. Abstract to 136 words; m/K -> (N/K) p_i; eq. (9) underbrace
labels at 9 pt; Algorithm 1 line 8 split so nothing wraps; Table 1 header "blind avg."; balanced
last page; e-mail lines at 9 pt. Record only; already applied."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF, PS, ES = "main_fit.tex", "sections/proposed_solution_short.tex", "sections/experiments_short.tex"

def rd(rel): return (ROOT / rel).read_text(encoding="utf-8")
def wr(rel, s): (ROOT / rel).write_text(s, encoding="utf-8", newline="\n")
def sub(rel, old, new):
    s = rd(rel); assert s.count(old) == 1, (rel, old[:60], s.count(old)); wr(rel, s.replace(old, new))

ABS_NEW = r"""\begin{abstract}
Minibatch stochastic gradient descent (SGD) is group-blind: a batch contains
each group in proportion to its prevalence, not to its weight in the
objective, so SGD optimizes a prevalence-weighted surrogate. Reading a
minibatch as a partial-participation event over groups, we carry the masked
optimal transport construction of \textsf{FedAVOT} across: aligning the
batch-composition law $q$ with the target importance $p$ yields per-batch
group weights whose stochastic subgradient is exactly unbiased, at the
$O(1/\sqrt{T})$ rate. Alignment is feasible under a Hall-type condition;
past it, Sinkhorn returns an information projection with closed-form
residual, splitting the excess risk into an instance-fixed alignment gain
and an optimization residual paid by the estimator. A sweep over eleven
availability skews on Adult and IMDb-Wiki shows the two crossing where the
decomposition predicts. A mean--conditional-value-at-risk (CVaR) layer
reaches the worst group at rate $O(\kappa(\alpha,\gamma)/\sqrt{T})$.
\end{abstract}"""

EDITS = [
 (ES, "$m/K$; \\emph{full}, every group every step weighted by $p$.",
      "with weights $(N/K)\\,p_i$ on the observed groups \\cite{rahimi2025fedavot};\n\\emph{full}, every group every step weighted by $p$."),
 (ES, "The fixed multiplier $m/K$ reaches $0.670$ and $8504$", "The fixed multiplier $(N/K)\\,p_i$ reaches $0.670$ and $8504$"),
 (ES, "Instance & \\avot{} & unif.\\ avg & upsamp. & LDS & full \\\\", "Instance & \\avot{} & blind avg. & upsamp. & LDS & full \\\\"),
 (PS, "_{\\text{alignment floor}}", "_{\\textnormal{\\small alignment floor}}"),
 (PS, "_{\\text{optimization residual}}", "_{\\textnormal{\\small optimization residual}}"),
 (PS, "  \\State $t^{t}\\leftarrow t^{t-1}-\\eta(1-\\gamma)\\big(1-\\tfrac{1}{\\alpha}\\sum_{i\\in A^t}Y[i,j(t)]\\mathbf{1}\\{\\hat f^t_i>t^{t-1}\\}\\big)$",
      "  \\State $\\delta^t\\leftarrow 1-\\tfrac{1}{\\alpha}\\sum_{i\\in A^t}Y[i,j(t)]\\mathbf{1}\\{\\hat f^t_i>t^{t-1}\\}$\n  \\State $t^{t}\\leftarrow t^{t-1}-\\eta(1-\\gamma)\\,\\delta^t$"),
 (MF, "averaged (lines 6 and 8 of Algorithm~\\ref{alg:gavot}).", "averaged (lines 6, 8 and 9 of Algorithm~\\ref{alg:gavot})."),
 (MF, "\\usepackage{url}", "\\usepackage{url}\n\\usepackage{balance}"),
 (MF, "\\begin{thebibliography}", "\\balance\n\\begin{thebibliography}"),
 (MF, "\\texttt{\\{herlock.rahimi, dionysis.kalogerias\\}@yale.edu}\\\\", "{\\normalsize\\texttt{\\{herlock.rahimi, dionysis.kalogerias\\}@yale.edu}}\\\\"),
 (MF, "\\texttt{\\{vihaan.goyal1512, amtejsodhi\\}@gmail.com}}", "{\\normalsize\\texttt{\\{vihaan.goyal1512, amtejsodhi\\}@gmail.com}}}"),
]

if __name__ == "__main__":
    s = rd(MF)
    a, b = s.index("\\begin{abstract}"), s.index("\\end{abstract}") + len("\\end{abstract}")
    wr(MF, s[:a] + ABS_NEW + s[b:])
    for rel, old, new in EDITS:
        sub(rel, old, new)
    assert "the \\emph{fixed multiplier}" in rd(ES)
    body = ABS_NEW.split("\n", 1)[1].rsplit("\n", 1)[0]
    words = len(re.sub(r"\\[a-zA-Z]+|[{}$\\]", " ", body).split())
    print("ok; abstract words ~", words)
