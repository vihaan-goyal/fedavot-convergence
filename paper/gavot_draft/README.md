# GAVOT draft (Herlock's 2026-09-15 ICASSP draft) and our work on it

Herlock's paper "Group-Fair Stochastic Gradient Descent via Masked Optimal Transport"
(method renamed GAVOT; FedAVOT kept in figures). Nothing here is on his Overleaf; he merges
what he wants. His files are never edited in place: the zip he sent is kept verbatim in
`original/`, and every version of ours is a separate file.

## Layout

    original/                 Herlock's zip, byte for byte (main.tex, spconf.sty, figs/, his README)
    original_README_from_zip.md   his README again, at top level for visibility

    main.tex                  his draft + our correctness pass (12 edits, see review/CHANGELIST.md);
                              compiles to 4 pages + references on page 5
    sections/
      problem_formulation.tex   fresh Sec. 2, structure of FedAVOT Sec. 1 + CAMSAP Sec. 2
      proposed_solution.tex     fresh Sec. 3, structure of FedAVOT Secs. 2-3
      experiments_full.tex      his verified Sec. 5 + protocol + closed-form validation (E6)
    appendix.tex              one-page appendix (proofs, closed-form numbers, Adult tables);
                              nothing in the main text depends on it
    appendix_standalone.tex   wrapper that compiles the appendix alone (page 1 = stub labels)

    main_rewrite.tex          his paper with sections/ 2 and 3 dropped in       (6 pages)
    main_full.tex             his paper with sections/ 2, 3 and 5 dropped in    (7 pages, the EXTENDED version)
    main_fit.tex              same with sections/*_short.tex + the appendix     (4.3 pages + refs + 1 appendix page)
                              nothing is dropped: review/CUT_LEDGER.md maps every cut item to the
                              appendix or to main_full; tools/check_cut.py verifies no new numbers and
                              no lost labels; review/HERLOCK_TRIM_SUGGESTIONS.md lists the ~0.35 page
                              in his own sections that would close the remaining gap
    *_standalone.tex          one section each, no bibliography, cross-refs from main_full
    build.sh                  compiles all seven and moves the PDFs into pdf/
    pdf/                      the compiled PDFs (committed so nobody needs LaTeX to read them)

    figs/                     his figures + our regenerated severity_imdb.pdf (vector, his notation)
    review/
      section2_check.md, section3_check.md, section5_check.md   claim-by-claim audits of his draft
      section5_numbers.txt    the recomputed Sec. 5 numbers from results/
      CHANGELIST.md           what the correctness pass changed and why
      diff_vs_original.txt    unified diff, original/main.tex -> main.tex
      PASTE_FOR_HERLOCK.md    the same 12 edits as find/replace blocks for his Overleaf
      REWRITE_NOTES.md        what the fresh sections contain, page budget, cut list
      plain_text_sections.txt the three fresh sections as plain prose (no LaTeX)
    tools/
      make_standalones.py     builds the *_standalone.tex wrappers from main_full.aux
      detex.py                writes review/plain_text_sections.txt
      make_paste.py           writes review/PASTE_FOR_HERLOCK.md from the diff
      history/                the one-shot scripts that produced main.tex and sections/ (record only)

## Build

    cd paper/gavot_draft && ./build.sh        # MiKTeX pdflatex on PATH; two passes each, no bibtex

`spconf.sty` is his local stand-in; replace with the official ICASSP file before submission.

## Status (2026-09-16)

- Correctness pass: applied in `main.tex`, fits 4 + 1 pages. Fixes: Table 1 fixed-multiplier
  entry (0.670, not "div."), "diverges on every instance", the IMDb target description, the
  missing setup details, (p,r,E) -> (p,q,E), the Thm. 10 residual bound, the KL direction for
  the infeasible Sinkhorn limit (Gietl & Reffel 2013 added).
- Fresh Secs. 2, 3, 5: written, compile with zero undefined references, about one page over
  the 4-page limit even with four proofs moved to the appendix. Cut list in REWRITE_NOTES.md.
- Herlock's 9/15 metric request: lead with the loss on the least represented group rather
  than the overall objective. Built 2026-09-17 from the existing run CSVs by
  `scripts/pipeline/plot_rare_group.py` -> `figures/2026-09-17_rare_group/` (figures
  `rare_group_adult.*`, `rare_group_imdb.*`, copies in `figs/`; numbers in
  `rare_group_headline.md`). Rare group = Adult race "Other" (also Amer-Indian), IMDb tier 1
  (20 top-importance identities, least observed for beta > 0). Decay, headline cells:
  Adult prevalence Other CE .073 (GAVOT) vs .119 (group-blind) vs .031 (full); Adult aligned
  .031 vs .035 vs .031; IMDb skewed tier-1 MSE 77.0 vs 86.4 vs 72.2; IMDb aligned 73.6 vs
  79.9 vs 72.2. GAVOT wins the rare group on every Adult skew and on IMDb up to nu = .70,
  loses at the three most infeasible IMDb skews (same crossover as the overall objective).
  Accuracy would need a rerun (runner logs loss only).
- Open for Herlock: appendix page allowed?, exact-penalty arXiv number (his FILLIN), t-stat
  convention (population std kept), whether E5/CVaR stays.
