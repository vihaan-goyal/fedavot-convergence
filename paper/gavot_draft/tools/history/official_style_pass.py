"""One-shot (2026-09-21): after installing the official ICASSP 2027 spconf.sty. (1) Author block
fits the 178 mm text width (\\quad between names, e-mails grouped). (2) Vihaan: one version of the
paper only, no "extended version" pointers (removed earlier the same day); the official style
leaves ~half a column free on page 4, so the clauses cut for space on 9/21 go back in. (3) One
overfull line in Thm. 8. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF, PF, PS, ES = "main_fit.tex", "sections/problem_formulation_short.tex", \
    "sections/proposed_solution_short.tex", "sections/experiments_short.tex"

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

EDITS = [
 (MF, r"\name{Herlock (SeyedAbolfazl) Rahimi \qquad Amtej Sodhi \qquad Vihaan Goyal \qquad Dionysis Kalogerias%",
      r"\name{Herlock (SeyedAbolfazl) Rahimi \quad Amtej Sodhi \quad Vihaan Goyal \quad Dionysis Kalogerias%"),
 (MF, r"\texttt{\{herlock.rahimi, dionysis.kalogerias\}@yale.edu, vihaan.goyal1512@gmail.com, amtejsodhi@gmail.com}}",
      r"\texttt{\{herlock.rahimi, dionysis.kalogerias\}@yale.edu}, \texttt{\{vihaan.goyal1512, amtejsodhi\}@gmail.com}}"),
 # Thm. 8 overfull line
 (PS, "$\\Phi(w)\\triangleq F_p\\big(\\argmin_{\\mathcal{C}} F_w\\big)$ for the $p$-risk of\nthe minimizer of the $w$-weighted risk. Then",
      "$\\Phi(w)\\triangleq F_p(\\argmin_{\\mathcal{C}} F_w)$, the $p$-risk of the\nminimizer of the $w$-weighted risk. Then"),
 # restore clauses cut for space (fit_squeeze4 / icassp_kit_compliance2-3)
 (ES, "helps: the grid's best rare-group loss is at $\\gamma{=}1$ on all four\nheadline instances. CVaR tilts",
      "helps: the grid's best rare-group loss is at $\\gamma{=}1$ on all four\nheadline instances, and $(0.1,0.1)$ nearly triples the loss on Other\n($.207$ against $.073$) and lifts the IMDb-Wiki top identities from $77.0$\nto $103$. CVaR tilts"),
 (ES, "$p_i/r_i$ large and amplifies variance, not alignment.",
      "$p_i/r_i$ large and amplifies variance, not alignment. Risk aversion changes\nthe functional, not who is observed."),
 (ES, "three of five skews and exceeds it at the two most infeasible ($.0210$\nagainst $.0110$, $.0181$ against $.0144$).",
      "three of five skews ($.0134$ against $.0129$, $.0050$ against $.0049$,\n$.0002$ against $.0003$) and exceeds it at the two most infeasible ($.0210$\nagainst $.0110$, $.0181$ against $.0144$)."),
 (ES, "$.035$ aligned, matching full. On IMDb-Wiki",
      "$.035$ aligned, matching full; Amer-Indian behaves the same way. On\nIMDb-Wiki"),
 (ES, "identity on IMDb-Wiki, $253$ against $331$ at $\\nu{=}.31$ (full $219$).",
      "identity on IMDb-Wiki, $253$ against $331$ at $\\nu{=}.31$ (full $219$; a\n$30$-image group, $\\pm5$ to $10$ across seeds)."),
 (ES, "dashed floors, and what remains is the residual, $2.3$ at $\\nu{=}.88$, the\none significant loss.",
      "dashed floors, and what remains is the residual, $2.3$ at $\\nu{=}.88$, the\none significant loss. Transport helps exactly while there is mass left to move."),
 (ES, "predicts when $\\tilde p=p$. Self-normalized upsampling, the",
      "predicts when $\\tilde p=p$. The fixed multiplier diverges on both aligned\ninstances and is far off on the other two. Self-normalized upsampling, the"),
 (PS, "once, offline. Since",
      "once, offline; training then adds one lookup and one multiply per group per\nstep. Since"),
 (PF, "since $\\tilde p_i\\le r_i$ always. The question of \\cite{rahimi2025fedavot},\nread on batches:",
      "since $\\tilde p_i\\le r_i$ always, and upscaling the examples that do appear\ndestabilizes the iterates \\cite{rahimi2025fedavot}. The question, read on\nbatches:"),
]

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    print("ok")
