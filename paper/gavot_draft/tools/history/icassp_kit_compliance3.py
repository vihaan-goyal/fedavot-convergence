"""One-shot (2026-09-21, after icassp_kit_compliance2.py): last page-budget trims after the
column-width figures went in; every removed clause is stated elsewhere in the paper or lives in
the _full sections. Record only; already applied."""
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
 (ES, "$.035$ aligned, matching full; Amer-Indian behaves the same way. On\nIMDb-Wiki",
      "$.035$ aligned, matching full. On IMDb-Wiki"),
 (ES, "identity on IMDb-Wiki, $253$ against $331$ at $\\nu{=}.31$ (full $219$; a\n$30$-image group, $\\pm5$ to $10$ across seeds).",
      "identity on IMDb-Wiki, $253$ against $331$ at $\\nu{=}.31$ (full $219$)."),
 (ES, "predicts when $\\tilde p=p$. The fixed multiplier diverges on both aligned\ninstances and is far off on the other two. Self-normalized upsampling, the",
      "predicts when $\\tilde p=p$. Self-normalized upsampling, the"),
 (PS, "once, offline; training then adds one lookup and one multiply per group per\nstep. Since",
      "once, offline. Since"),
 (PF, "since $\\tilde p_i\\le r_i$ always, and upscaling the examples that do appear\ndestabilizes the iterates \\cite{rahimi2025fedavot}. The question, read on\nbatches:",
      "since $\\tilde p_i\\le r_i$ always. The question of \\cite{rahimi2025fedavot},\nread on batches:"),
 (MF, "\\cite{rahimi2025fedavot}. Label-distribution smoothing \\cite{yang2021dir}\nre-weights by label rarity, not by how rarely a group is observed.",
      "\\cite{rahimi2025fedavot}."),
 (PS, "   node distance=1.5mm,", "   node distance=1.2mm,"),
]

if __name__ == "__main__":
    for rel, old, new in EDITS:
        sub(rel, old, new)
    print("ok")
