"""One-shot (2026-09-21): ICASSP 2027 paper-kit compliance for main_fit.tex
(https://cmsworkshops.com/ICASSP2027/papers/paper_kit.php): no appendix page (page 5 = references
only), title in capitals, no page numbers, no font below 9 pt in text/tables/captions, abstract
100-150 words, Table 1 m/K column moved into its caption. Pointers to the appendix now point to
the extended version (main_full.tex). Record only; already applied."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF, PF, PS, ES = "main_fit.tex", "sections/problem_formulation_short.tex", \
    "sections/proposed_solution_short.tex", "sections/experiments_short.tex"

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

ABS_NEW = r"""\begin{abstract}
Minibatch SGD is group-blind: which groups appear in a batch is decided by
their prevalence in the data, not by how much they are meant to count in the
objective, so the iterates converge to a prevalence-weighted surrogate rather
than to the target risk. A minibatch is a partial-participation event over
groups, so we carry the masked optimal transport construction of
\textsf{FedAVOT} across: aligning the batch-composition law $q$ with the
target importance $p$ yields per-batch group weights whose stochastic
subgradient is exactly unbiased, with the standard $O(1/\sqrt{T})$ rate and a
constant independent of batch coverage. Alignment is feasible under a
Hall-type condition, importance not exceeding observation rate; past it,
Sinkhorn returns an information projection whose residual we compute in
closed form, splitting the excess risk into an alignment gain fixed by the
instance and an optimization residual paid by the estimator. A sweep over
eleven availability skews on Adult and IMDb-Wiki shows the two crossing where
the decomposition predicts. A mean--CVaR layer on top reaches the worst group
at rate $O(\kappa(\alpha,\gamma)/\sqrt{T})$.
\end{abstract}"""

EDITS = [
 (MF, r"\title{Group-Fair Stochastic Gradient Descent \\ via Masked Optimal Transport}",
      r"\title{GROUP-FAIR STOCHASTIC GRADIENT DESCENT \\ VIA MASKED OPTIMAL TRANSPORT}"),
 (MF, "\\maketitle\n", "\\maketitle\n\\pagestyle{empty}\\thispagestyle{empty}\n"),
 (MF, "\\clearpage\n\\input{appendix}", "% appendix removed: ICASSP allows references only on page 5; see main_full.tex"),
 (ES, "\\footnotesize\\setlength{\\tabcolsep}{2.2pt}\n\\begin{tabular}{lcccccc}",
      "\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{lccccc}"),
 (ES, r"Instance & \avot{} & unif.\ avg & upsamp. & LDS & $m/K$ & full \\",
      r"Instance & \avot{} & unif.\ avg & upsamp. & LDS & full \\"),
 (ES, r"& $0.2288$ & -- & $0.670$ & $0.2073$ \\", r"& $0.2288$ & -- & $0.2073$ \\"),
 (ES, r"& $0.2075$ & -- & div. & $0.2073$ \\", r"& $0.2075$ & -- & $0.2073$ \\"),
 (ES, r"& $86.74$ & $94.28$ & $8504$ & $82.95$ \\", r"& $86.74$ & $94.28$ & $82.95$ \\"),
 (ES, r"& $84.40$ & $89.43$ & div. & $82.95$ \\", r"& $84.40$ & $89.43$ & $82.95$ \\"),
 (ES, "batch; LDS \\cite{yang2021dir}: label-distribution smoothing, regression only;\n$m/K$ diverges under non-uniform observation.}",
      "batch; LDS \\cite{yang2021dir}: label-distribution smoothing, regression only.\nThe fixed multiplier $m/K$ reaches $0.670$ and $8504$ on the two infeasible\ninstances and diverges on the aligned ones.}"),
 (ES, "steps, $5$ seeds, $F_p$ over the last $500$ steps. Floors are exact; full\nprotocol and closed-form check in the appendix, unabridged discussion in the\nextended version.",
      "steps, $5$ seeds, $F_p$ over the last $500$ steps. Floors are exact; full\nprotocol, proofs, closed-form check and unabridged discussion are in the\nextended version."),
 (ES, "crosses it. Adult: appendix.}", "crosses it. Adult skews: extended version.}"),
 (ES, "$\\nu{=}.88$, appendix). Transport", "$\\nu{=}.88$, extended version). Transport"),
 (ES, "(per-race table in the appendix). On", "(per-race table in the extended version). On"),
 (PF, "(Proof in the appendix.)", "(Proof in the extended version.)"),
 (PS, "by flow duality (proofs in the appendix).", "by flow duality (proofs in the extended version)."),
 (PS, "support \\cite{sinkhorn1967,cuturi2013,peyre2019} (appendix, \\eqref{eq:ipfp}),",
      "support \\cite{sinkhorn1967,cuturi2013,peyre2019},"),
 (PS, "font=\\tiny,fill=Periwinkle!20", "font=\\scriptsize,fill=Periwinkle!20"),
 (PS, "font=\\tiny,fill=YellowOrange!20", "font=\\scriptsize,fill=YellowOrange!20"),
 (PS, "lbl/.style={font=\\tiny\\itshape}", "lbl/.style={font=\\scriptsize\\itshape}"),
 (PS, "{$g_4$ \\tiny(rare)}", "{$g_4$ (rare)}"),
 (ES, "\\includegraphics[width=0.82\\columnwidth]{figs/severity_imdb.pdf}", "\\includegraphics[width=\\columnwidth]{figs/severity_imdb.pdf}"),
 (ES, "\\includegraphics[width=0.86\\columnwidth]{figs/rare_group_fit.pdf}", "\\includegraphics[width=\\columnwidth]{figs/rare_group_fit.pdf}"),
]

if __name__ == "__main__":
    s = (ROOT / MF).read_text(encoding="utf-8")
    a, b = s.index("\\begin{abstract}"), s.index("\\end{abstract}") + len("\\end{abstract}")
    s = s[:a] + ABS_NEW + s[b:]
    (ROOT / MF).write_text(s, encoding="utf-8", newline="\n")
    for rel, old, new in EDITS:
        sub(rel, old, new)
    words = len(re.sub(r"\\[a-zA-Z]+|[{}$]", " ", ABS_NEW.split("\n", 1)[1].rsplit("\n", 1)[0]).split())
    print("ok; abstract words ~", words)
