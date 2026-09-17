# Group-Fair SGD via Masked Optimal Transport -- ICASSP submission

Upload this whole zip to Overleaf ("New Project" -> "Upload Project").
Set the main document to `main.tex` and the compiler to **pdfLaTeX**.
Two passes are needed for cross-references; Overleaf does this automatically.

## Contents

    main.tex        the paper (4 pages + 1 page references)
    spconf.sty      *** LOCAL STAND-IN -- REPLACE BEFORE SUBMITTING ***
    figs/
      severity_imdb.png         Figure 2 (the only figure main.tex includes)
      severity_adult.png        Adult half of the severity sweep, unused
      adult_race_decay.pdf      full Adult figure from the results package
      imdb_infeas_decay.pdf     full IMDb infeasible figure
      imdb_feas_decay.pdf       full IMDb feasible figure
      severity_sweep_table.csv  numbers behind Table 2

## Before submitting

1. **Replace `spconf.sty`.** The file here is a stand-in written to reproduce
   the ICASSP page geometry so the draft paginates correctly. Delete it and
   upload the official `spconf.sty` from the ICASSP author kit. `main.tex`
   needs no change. One known difference: the `\thanks{}` funding footnote does
   not render under the stand-in (footnotes inside `\twocolumn[]` do not work
   in vanilla LaTeX); check that it appears once the real style file is in.

2. **Sweep the `%%FILLIN` markers** in `main.tex` (search for `%%FILLIN`).

3. **Bibliography.** References are an inline `thebibliography` environment at
   the end of `main.tex`, so no `.bib` or `bibtex` pass is required. If you
   prefer `IEEEbib.bst`, replace that block with `\bibliography{refs}` and add
   `IEEEbib.bst` plus your `refs.bib`.

4. **Reference [6]** (the FedAVOT paper) and **[15]** (the exact-penalty
   companion) both need final venue/arXiv numbers.

## Unused figures

`main.tex` includes only `figs/severity_imdb.png`. The other files are the
remaining figures from the 2026-09-15 results package, kept here so you can
swap one in without re-exporting. Each is roughly 14 lines of column space, so
adding one means cutting about that much prose.
