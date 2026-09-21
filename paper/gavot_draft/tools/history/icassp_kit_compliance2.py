"""One-shot (2026-09-21, after icassp_kit_compliance.py): abstract to ~150 words and ~14 lines of
trims so the column-width figures fit in 4 pages. Removed clauses live in the _full sections.
Record only; already applied."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
MF, PS, ES = "main_fit.tex", "sections/proposed_solution_short.tex", "sections/experiments_short.tex"

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

ABS_NEW = r"""\begin{abstract}
Minibatch SGD is group-blind: which groups appear in a batch is decided by
their prevalence in the data, not by how much they are meant to count in the
objective, so SGD optimizes a prevalence-weighted surrogate. A minibatch is a
partial-participation event over groups, so we carry the masked optimal
transport construction of \textsf{FedAVOT} across: aligning the
batch-composition law $q$ with the target importance $p$ yields per-batch
group weights whose stochastic subgradient is exactly unbiased, at the
standard $O(1/\sqrt{T})$ rate. Alignment is feasible under a Hall-type
condition; past it, Sinkhorn returns an information projection whose
residual we compute in closed form, splitting the excess risk into an
alignment gain fixed by the instance and an optimization residual paid by
the estimator. A sweep over eleven availability skews on Adult and IMDb-Wiki
shows the two crossing where the decomposition predicts. A mean--CVaR layer
on top reaches the worst group at rate $O(\kappa(\alpha,\gamma)/\sqrt{T})$.
\end{abstract}"""

EDITS = [
 # E5: the (0.1,0.1) sentence -> extended version
 (ES, "helps: the grid's best rare-group loss is at $\\gamma{=}1$ on all four\nheadline instances, and $(0.1,0.1)$ nearly triples the loss on Other\n($.207$ against $.073$) and lifts the IMDb-Wiki top identities from $77.0$\nto $103$. CVaR tilts",
      "helps: the grid's best rare-group loss is at $\\gamma{=}1$ on all four\nheadline instances. CVaR tilts"),
 # E3 tighten
 (ES, "three of five skews ($.0134$ against $.0129$, $.0050$ against $.0049$,\n$.0002$ against $.0003$) and exceeds it at the two most infeasible ($.0210$\nagainst $.0110$, $.0181$ against $.0144$).",
      "three of five skews and exceeds it at the two most infeasible ($.0210$\nagainst $.0110$, $.0181$ against $.0144$)."),
 # E4 tighten
 (ES, "Transport still concentrates weight on a starved\ngroup whenever it appears, $p_i/r_i$ times its batch share:\nLemma~\\ref{lem:variance} bounds the second moment identically for both\nrules, but the variance about the mean is larger, and at constant stepsize\nthe iterates sit on a noise floor proportional to it.",
      "Transport still concentrates weight on a starved\ngroup whenever it appears, so its variance about the mean is larger\n(Lemma~\\ref{lem:variance} bounds only the second moment), and at constant\nstepsize the iterates sit on a noise floor proportional to it."),
 # protocol tighten
 (ES, "Each step observes $K{=}3$ groups drawn\n$\\propto r$, each taking $H{=}5$ local steps before the weighted average,\nfor every rule alike:",
      "Each step observes $K{=}3$ groups drawn\n$\\propto r$, each taking $H{=}5$ local steps before the weighted average:"),
 # Sec 3 coupling paragraph tighten
 (PS, "Requiring the weights to be\na probability vector on each realized composition and to reproduce $p$ in\nexpectation is the \\emph{masked optimal transport} (MOT) feasibility problem\nof \\cite{rahimi2025fedavot},",
      "Weights that form a probability vector on each realized composition and\nreproduce $p$ in expectation are the \\emph{masked optimal transport} (MOT)\nfeasibility problem of \\cite{rahimi2025fedavot},"),
 # contributions item 1 tighten
 (MF, "\\item \\emph{The reduction} (Sec.~\\ref{sec:setup}). Group-blind minibatch SGD reduces, under\nuniform-within-batch averaging, to agnostic \\textsf{FedAvg} with one local step, so the surrogate identity of\n\\cite{rahimi2025agnostic} names the function SGD actually minimizes, and\ntransport weights make the batch subgradient exactly unbiased for $\\nabla F_p$\n(Lemma~\\ref{lem:unbiased}).",
      "\\item \\emph{The reduction} (Sec.~\\ref{sec:setup}). Group-blind minibatch SGD is\nagnostic \\textsf{FedAvg} with one local step, so \\cite{rahimi2025agnostic} names\nthe function it minimizes, and transport weights make the batch subgradient\nexactly unbiased for $\\nabla F_p$ (Lemma~\\ref{lem:unbiased})."),
]

if __name__ == "__main__":
    s = (ROOT / MF).read_text(encoding="utf-8")
    a, b = s.index("\\begin{abstract}"), s.index("\\end{abstract}") + len("\\end{abstract}")
    s = s[:a] + ABS_NEW + s[b:]
    (ROOT / MF).write_text(s, encoding="utf-8", newline="\n")
    for rel, old, new in EDITS:
        sub(rel, old, new)
    body = ABS_NEW.split("\n", 1)[1].rsplit("\n", 1)[0]
    words = len(re.sub(r"\\[a-zA-Z]+|[{}$\\]", " ", body).split())
    print("ok; abstract words ~", words)
