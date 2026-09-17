import io, re
import os
D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
NL = chr(10)

def detex(s):
    s = re.sub(r"(?m)^%.*\n", "", s)
    s = re.sub(r"(?<!\\)%.*", "", s)
    for env in ["figure", "figure*", "table", "table*", "algorithm", "tikzpicture", "center"]:
        e = re.escape(env)
        s = re.sub(r"\\begin\{" + e + r"\}.*?\\end\{" + e + r"\}", "", s, flags=re.S)
    s = re.sub(r"\\section\*?\{([^}]*)\}", lambda m: NL + "=== " + m.group(1).upper() + " ===" + NL, s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\cite\[[^\]]*\]\{[^}]*\}", "", s)
    s = re.sub(r"\\cite\{[^}]*\}", "", s)
    s = re.sub(r"(Sec\.|Fig\.|Thm\.|Cor\.|Lemma|Theorem|Proposition|Corollary|Table|Algorithm|Assumption)~\\(?:eq)?ref\{[^}]*\}",
               lambda m: {"Sec.": "the section", "Fig.": "the figure", "Thm.": "the theorem", "Cor.": "the corollary",
                          "Table": "the table", "Algorithm": "the algorithm"}.get(m.group(1), "the " + m.group(1).lower()), s)
    s = re.sub(r"\\eqref\{[^}]*\}", "the equation", s)
    s = re.sub(r"\\ref\{[^}]*\}", "", s)
    def env_head(m):
        kind = m.group(1).capitalize()
        title = m.group(2)
        return NL + kind + (" (" + title + ")" if title else "") + ". "
    s = re.sub(r"\\begin\{(theorem|lemma|proposition|corollary|assumption|remark)\}(?:\[([^\]]*)\])?", env_head, s)
    s = re.sub(r"\\end\{(theorem|lemma|proposition|corollary|assumption|remark)\}", NL, s)
    s = re.sub(r"\\begin\{proof\}(?:\[([^\]]*)\])?", lambda m: NL + "Proof" + (" (" + m.group(1) + ")" if m.group(1) else "") + ". ", s)
    s = re.sub(r"\\end\{proof\}", NL, s)
    s = re.sub(r"\\begin\{equation\}", NL + "    ", s)
    s = re.sub(r"\\end\{equation\}", NL, s)
    s = s.replace(r"\[", NL + "    ").replace(r"\]", NL)
    for cmd in ["textbf", "emph", "textsf", "textit", "text", "mathrm", "mathbf", "mathcal", "underbrace"]:
        s = re.sub(r"\\" + cmd + r"\{([^{}]*)\}", r"\1", s)
        s = re.sub(r"\\" + cmd + r"\{([^{}]*)\}", r"\1", s)
    s = s.replace(r"\avotcvar{}", "GAVOT+CVaR").replace(r"\avot{}", "GAVOT").replace(r"\avot", "GAVOT")
    s = s.replace(r"\noindent", "").replace(r"\medskip", "").replace(r"\clearpage", "")
    s = s.replace("~", " ").replace(r"\,", " ").replace(r"\;", " ").replace(r"\!", "").replace(r"\ ", " ")
    s = s.replace("``", '"').replace("''", '"').replace("---", " - ").replace("--", "-")
    s = re.sub(r"\\best\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(tfrac|frac)\{([^{}]*)\}\{([^{}]*)\}", r"(\2)/(\3)", s)
    s = re.sub(r"\\(big|Big|bigg|left|right)", "", s)
    s = re.sub(r"\\(triangleq)", "=", s)
    s = re.sub(r"\\(le|leq)\b", "<=", s); s = re.sub(r"\\(ge|geq)\b", ">=", s)
    s = re.sub(r"\\(to|rightarrow)\b", "->", s); s = re.sub(r"\\(times)\b", "x", s)
    s = re.sub(r"\\(hat|bar|tilde|widehat)\s*\{?([A-Za-z\\]+)\}?", r"\2_\1", s)
    words = {"subseteq": " ⊆ ", "subset": " ⊂ ", "in": " ∈ ", "notin": " ∉ ", "ni": " ∋ ", "sim": " ~ ",
             "propto": " ∝ ", "sum": " Σ ", "qquad": "    ", "quad": "  ", "cdot": "·", "times": " × ",
             "infty": "∞", "partial": "∂", "nabla": "∇", "ell": "ℓ", "theta": "θ", "eta": "η", "pi": "π",
             "nu": "ν", "beta": "β", "alpha": "α", "gamma": "γ", "kappa": "κ", "varepsilon": "ε",
             "epsilon": "ε", "Phi": "Φ", "Delta": "Δ", "mid": " | ", "langle": "<", "rangle": ">",
             "top": "ᵀ", "star": "*", "dagger": "†", "oslash": " ⊘ ", "exists": "∃", "forall": "∀",
             "argmin": "argmin", "E": "E", "PP": "P", "R": "R", "Nn": "", "simplex": "Δ", "KL": "KL",
             "Proj": "Proj", "dots": "...", "ldots": "...", "iff": "iff", "ge": ">=", "le": "<=",
             "neq": "≠", "ne": "≠", "circ": "∘", "mathbf": "", "boldsymbol": "", "hfill": "", "square": "□"}
    s = re.sub(r"\\([A-Za-z]+)", lambda m: words.get(m.group(1), m.group(1)), s)
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\$+", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", NL + NL, s)
    return s.strip() + NL

out = []
for name, title in [("problem_formulation", "SECTION 2: PROBLEM FORMULATION"),
                    ("proposed_solution", "SECTION 3: PROPOSED APPROACH"),
                    ("experiments_full", "SECTION 5: EXPERIMENTS")]:
    body = io.open(os.path.join(D, "sections", name + ".tex"), encoding="utf-8").read()
    out.append("#" * 70 + NL + "# " + title + NL + "#" * 70 + NL + NL + detex(body))
txt = (NL + NL).join(out)
io.open(D + r"\review\plain_text_sections.txt", "w", encoding="utf-8", newline=NL).write(txt)
print(len(txt.split()), "words")
