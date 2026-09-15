# ICASSP-length version (2026-09-15)

`complete_short.tex` is Herlock's `complete.tex` (the 11-page long version with the 2026-09-14
results, saved here as `complete_long_2026-09-15.tex`) cut to the 4+1 page limit by DELETING whole
blocks; retained prose is verbatim. `assemble_short.py` regenerates it from the long file
(edit the keep-ranges there, not the short tex). Dropped: related work, contributions list, ERM
derivation, examples, Sinkhorn algorithm box, main-theorem proof (sketch instead), remarks,
regularization subsection, synthetic sweep + mechanism figures, IMDb feasible figure, CVaR
paragraph, bias-validation paragraph. Class is Herlock's 9pt extarticle (ICASSP template is
10pt article; switching adds ~1 page).

Compile: pdflatex / bibtex / pdflatex x2 (MiKTeX or tectonic). Status at commit: 4 pages of content + references on page 5 (ICASSP 4+1), compiles clean.
