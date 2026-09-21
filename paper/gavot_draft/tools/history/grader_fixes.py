"""One-shot (2026-09-21): apply review/ICASSP_GRADE_2026-09-21.md, everything except deletions
(Vihaan: "fix all of it, don't do any of the stuff that requires deletion"). Uncited references are
cited where they belong instead of removed. Record only; already applied."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF, PF, PS, ES = "main_fit.tex", "sections/problem_formulation_short.tex", \
    "sections/proposed_solution_short.tex", "sections/experiments_short.tex"

def rd(rel): return (ROOT / rel).read_text(encoding="utf-8")
def wr(rel, s): (ROOT / rel).write_text(s, encoding="utf-8", newline="\n")
def sub(rel, old, new, count=1):
    s = rd(rel); assert s.count(old) == count, (rel, old[:60], s.count(old)); wr(rel, s.replace(old, new))

EDITS = [
 # B2 footnote 9 pt
 (MF, r"\thanks{This work is supported by NSF under Grant 2242215.}", r"\thanks{\small This work is supported by NSF under Grant 2242215.}"),
 # S4 acronyms
 (MF, "Minibatch SGD is group-blind: which groups appear in a batch is decided by", "Minibatch stochastic gradient descent (SGD) is group-blind: which groups\nappear in a batch is decided by"),
 (MF, "the decomposition predicts. A mean--CVaR layer\non top reaches the worst group", "the decomposition predicts. A mean--conditional-value-at-risk (CVaR) layer\non top reaches the worst group"),
 (ES, "regression \\cite{rothe2018imdbwiki}: linear regression on $128$-d face\nembeddings", "regression \\cite{rothe2018imdbwiki}: linear regression (mean-squared\nerror, MSE) on $128$-d face embeddings"),
 (PS, "marginal $\\hat p\\triangleq T\\mathbf{1}$ is KL-closest to $p$ over the", "marginal $\\hat p\\triangleq T\\mathbf{1}$ is Kullback--Leibler (KL) closest to $p$ over the"),
 # S1 cite the unused references where they belong
 (PS, "Existence is a supply--demand question on the bipartite graph $E$, settled\nby flow duality (proofs omitted for space).",
      "Existence is a supply--demand question on the bipartite graph $E$, settled\nby flow duality \\cite{hall1935,fordfulkerson1956} (proofs omitted for space)."),
 (MF, "so \\textsf{FedAvg} optimizes a surrogate whose weights are induced rather\nthan chosen \\cite{rahimi2025agnostic,wang2020objective,cho2022biased};",
      "so \\textsf{FedAvg} \\cite{mcmahan2017fedavg} and its heterogeneity-aware\nvariants \\cite{li2020fedprox,karimireddy2020scaffold} optimize a surrogate\nwhose weights are induced rather than chosen\n\\cite{rahimi2025agnostic,wang2020objective,cho2022biased};"),
 (MF, "\\cite{agarwal2018reductions,cotter2019twoplayer,chamon2020pacc};", "\\cite{agarwal2018reductions,cotter2019twoplayer,chamon2020pacc,chamon2023nonconvex};"),
 (MF, "\\cite{sagawa2020dro,hashimoto2018repeated,levy2020large} change the functional", "\\cite{sagawa2020dro,hashimoto2018repeated,levy2020large,namkoong2017variance,curi2020adaptive} change the functional"),
 (PS, "rests on \\cite[Lem.~1]{rahimi2025fedavot} moved from models to gradients:", "rests on \\cite[Lem.~1]{rahimi2025fedavot} moved from models to gradients and\non the classical projected-subgradient bound \\cite{nemirovski2009}:"),
 (MF, "mean--CVaR functional over groups on top of the transport weights\n\\cite{rahimi2025agnostic,rockafellar2000cvar}:", "mean--CVaR functional over groups on top of the transport weights\n\\cite{rahimi2025agnostic,rockafellar2000cvar,theodoropoulos2024restricted}:"),
 # S2 reference [15] wording (comment kept for Herlock)
 (MF, "RKHSs,'' 2026, submitted.", "RKHSs,'' submitted for publication, 2026."),
 # reference hygiene
 (MF, "B.~A. y~Arcas", "B.~Ag\\\"{u}era y Arcas"),
 (MF, "imbalanced regression,'' in \\emph{Proc. Int. Conf. Machine Learning (ICML)},\n2021.", "imbalanced regression,'' in \\emph{Proc. Int. Conf. Machine Learning (ICML)},\n2021, pp. 11842--11851."),
 (MF, "B.~Becker and R.~Kohavi, ``Adult,'' UCI Machine Learning Repository, 1996.", "B.~Becker and R.~Kohavi, ``Adult,'' UCI Machine Learning Repository, 1996.\n[Online]. Available: https://doi.org/10.24432/C5XW20"),
 # Fig. 1 TikZ fonts (B1) and node width
 (PS, "minimum width=9mm,minimum height=3.4mm,font=\\scriptsize,fill=Periwinkle!20", "minimum width=9mm,minimum height=3.6mm,font=\\footnotesize,fill=Periwinkle!20"),
 (PS, "minimum width=13mm,minimum height=3.4mm,font=\\scriptsize,fill=YellowOrange!20", "minimum width=15mm,minimum height=3.6mm,font=\\footnotesize,fill=YellowOrange!20"),
 (PS, "lbl/.style={font=\\scriptsize\\itshape}", "lbl/.style={font=\\footnotesize\\itshape}"),
 # algorithm line numbers at 9 pt
 (MF, "\\usepackage{algpseudocode}", "\\usepackage{algpseudocode}\n\\algrenewcommand{\\alglinenumber}[1]{\\small #1:}"),
]

def leading_zeros(s):
    # ".31" -> "0.31" when not preceded by a digit; never touches "1.5" or "82.95"
    return re.sub(r"(?<![\d])\.(\d{2,4})(?![\d])", r"0.\1", s)

def crossref_words(s):
    s = s.replace("Thm.~\\ref", "Theorem~\\ref").replace("Cor.~\\ref", "Corollary~\\ref")
    s = s.replace("Prop.~\\ref", "Proposition~\\ref").replace("Lem.~\\ref", "Lemma~\\ref")
    return s

def reorder_bib():
    main = rd(MF)
    body = re.sub(r"^\\input\{([^}]*)\}\s*$", lambda m: rd(m.group(1) if m.group(1).endswith(".tex") else m.group(1) + ".tex"), main, flags=re.M)
    a = body.index("\\begin{thebibliography}"); text = body[:a]
    text = re.sub(r"(?m)%.*$", "", text)
    order = []
    for m in re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^}]*)\}", text):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in order: order.append(k)
    i = main.index("\\begin{thebibliography}"); j = main.index("\\end{thebibliography}")
    head_end = main.index("\n", i) + 1
    bib = main[head_end:j]
    items = re.split(r"(?=\\bibitem\{)", bib)
    pre = items[0]; items = items[1:]
    byk = {re.match(r"\\bibitem\{([^}]*)\}", it).group(1): it.rstrip() + "\n\n" for it in items}
    missing = [k for k in order if k not in byk]; assert not missing, missing
    unused = [k for k in byk if k not in order]
    ordered = [byk[k] for k in order] + [byk[k] for k in unused]
    wr(MF, main[:head_end] + pre + "".join(ordered) + main[j:])
    return order, unused

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    for rel in (ES, PF, PS, MF):
        wr(rel, crossref_words(rd(rel)))
    wr(ES, leading_zeros(rd(ES)))
    order, unused = reorder_bib()
    print("ok; bib order", len(order), "unused after citing:", unused)
