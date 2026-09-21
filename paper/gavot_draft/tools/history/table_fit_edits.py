"""One-shot (2026-09-21, after baselines_edits.py): make the 7-column Table 1 fit the column
(footnotesize, shorter instance labels) and shorten the appendix baseline sentence so the
appendix stays on one page. Record only; already applied."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]

def sub(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old[:60], s.count(old))
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

if __name__ == "__main__":
    for f in ("sections/experiments_short.tex", "sections/experiments_full.tex"):
        sub(f, "\\setlength{\\tabcolsep}{2.4pt}\n\\begin{tabular}{lcccccc}",
               "\\footnotesize\\setlength{\\tabcolsep}{2.2pt}\n\\begin{tabular}{lcccccc}")
        sub(f, "Adult, prev.\\ ($\\nu{=}.60$) &", "Adult prev.\\ ($\\nu{=}.60$) &")
        sub(f, "Adult, aligned ($\\nu{=}0$)  &", "Adult align.\\ ($\\nu{=}0$) &")
        sub(f, "IMDb, skewed ($\\nu{=}.31$)  &", "IMDb skew ($\\nu{=}.31$)   &")
        sub(f, "IMDb, aligned ($\\nu{=}0$)   &", "IMDb align.\\ ($\\nu{=}0$)  &")
    sub("appendix.tex",
        "machine precision for the logistic loss. Baselines of Table~\\ref{tab:overall}:\n"
        "upsampling weights the observed groups $\\propto p_i/r_i$, downsampling\n"
        "$\\propto\\min(p_i/r_i,1)$, both renormalized within the batch; LDS\n"
        "\\cite{yang2021dir} weights each sample by the inverse of the Gaussian-smoothed\n"
        "age histogram (unit bins, kernel $5$, $\\sigma{=}2$, mean weight $1$),\n"
        "averaged within each group and renormalized within the batch.",
        "machine precision for the logistic loss. Baselines: upsampling weights\n"
        "$\\propto p_i/r_i$, downsampling $\\propto\\min(p_i/r_i,1)$, LDS \\cite{yang2021dir}\n"
        "the inverse Gaussian-smoothed age histogram (kernel $5$, $\\sigma{=}2$) averaged\n"
        "per group; each renormalized within the batch.")
    print("ok")
