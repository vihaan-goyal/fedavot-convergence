import io, re
import os
D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NL = chr(10)
main = io.open(D + r"\main.tex", encoding="utf-8").read()
pre = main[:main.index(r"\begin{document}")]
bib = main[main.index(r"\begin{thebibliography}"):main.index(r"\end{thebibliography}") + len(r"\end{thebibliography}")]

stub_env = {
    "sec:setup": r"\section*{stub}\label{sec:setup}", "sec:gavot": r"\section*{stub}\label{sec:gavot}",
    "sec:exp": r"\section*{stub}\label{sec:exp}", "sec:cvar": r"\section*{stub}\label{sec:cvar}",
    "prop:surrogate": r"\begin{proposition}\label{prop:surrogate}stub\end{proposition}",
    "thm:feas": r"\begin{theorem}\label{thm:feas}stub\end{theorem}",
    "cor:batchsize": r"\begin{corollary}\label{cor:batchsize}stub\end{corollary}",
    "lem:unbiased": r"\begin{lemma}\label{lem:unbiased}stub\end{lemma}",
    "lem:variance": r"\begin{lemma}\label{lem:variance}stub\end{lemma}",
    "thm:rate": r"\begin{theorem}\label{thm:rate}stub\end{theorem}",
    "thm:infeasible": r"\begin{theorem}\label{thm:infeasible}stub\end{theorem}",
    "alg:gavot": r"\begin{algorithm}\caption{stub}\label{alg:gavot}\end{algorithm}",
    "fig:mask": r"\begin{figure}\caption{stub}\label{fig:mask}\end{figure}",
    "fig:severity": r"\begin{figure}\caption{stub}\label{fig:severity}\end{figure}",
    "tab:overall": r"\begin{table}\caption{stub}\label{tab:overall}\end{table}",
    "tab:severity": r"\begin{table}\caption{stub}\label{tab:severity}\end{table}",
    "ass:std": r"\begin{assumption}\label{ass:std}stub\end{assumption}",
}
for eq in ["eq:target", "eq:surrogate-gap", "eq:ptilde", "eq:mot", "eq:hall", "eq:batchlaw",
           "eq:ipfp", "eq:rate", "eq:infeasible", "eq:meancvar", "eq:ru"]:
    stub_env[eq] = r"\begin{equation}\label{" + eq + r"}\end{equation}"

files = {"problem_formulation": "Sec. 2 Problem Formulation",
         "proposed_solution": "Sec. 3 Proposed Approach",
         "experiments_full": "Sec. 5 Experiments"}
for name, title in files.items():
    body = io.open(os.path.join(D, "sections", name + ".tex"), encoding="utf-8").read()
    defined = set(re.findall(r"\\label\{([^}]*)\}", body))
    used = set(re.findall(r"\\(?:ref|eqref)\{([^}]*)\}", body))
    # cross-section labels and citation numbers come from the full build's aux file,
    # so no stub page and no bibliography are needed
    aux = io.open(D + r"\main_full.aux", encoding="utf-8").read().split(NL)
    keep = []
    for l in aux:
        m = re.match(r"\\newlabel\{([^}]*)\}", l)
        if m and m.group(1) in (used - defined):
            keep.append(l)
        elif l.startswith(r"\bibcite"):
            keep.append(l)
    stubs = keep
    missing = sorted(k for k in used - defined if not any(("{" + k + "}") in l for l in keep))
    doc = (pre + NL.join(keep) + NL + r"\title{" + title + "}" + NL +
           r"\name{}\address{}" + NL + r"\begin{document}\ninept\maketitle" + NL +
           r"\input{" + name + "}" + NL + r"\end{document}" + NL)
    io.open(os.path.join(D, name + "_standalone.tex"), "w", encoding="utf-8", newline=NL).write(doc)
    print(name, "stubs:", len(stubs), "missing:", missing)
