# ICASSP 2027 format and conventions grade — GAVOT paper (2026-09-21)

Graded artefacts
- Source: `paper/gavot_draft/overleaf/main.tex` (821 lines, manual `thebibliography`, 36 entries)
- PDF: `paper/gavot_draft/pdf/main_fit.pdf` (5 pages, 440 KB, MiKTeX pdfTeX 1.40.28)
- Figures: `figs/severity_imdb.pdf` (184.6 x 50.8 mm native), `figs/rare_group_fit.pdf` (172.6 x 43.1 mm native), both placed at `width=\textwidth` (178 mm)
- Style: `paper/gavot_draft/spconf.sty` is byte-identical to `kit/spconf.sty` (`diff` clean)
- Rules: kit page `cmsworkshops.com/ICASSP2027/papers/paper_kit.php`, `kit/Template.tex`, `kit/spconf.sty`, plus IEEE/ICASSP conventions

## Summary: 0 HARD fails, 7 SOFT fails, 4 borderline (3 against HARD rules, 1 against a SOFT rule)

Nothing in the paper violates a kit rule outright. Three HARD rules are borderline (sub-9pt text inside figures, the 8pt funding footnote, the reference numbering that is neither alphabetical nor first-appearance), one is a submission-time action (rename the file to `Rahimi.pdf`, register ORCiDs). The SOFT list is reference hygiene (10 never-cited entries, one "submitted" entry with a `%%FILLIN`), a legend that covers data in Fig. 3, and small consistency slips.

---

## 1. Borderline items against HARD rules (fix before submission)

### B1. Text inside figures is below 9 pt (kit: "no smaller than 9 points throughout the paper, including figure captions")
Measured from the figure PDFs and their placement scale (`severity_imdb` scaled 0.964x, `rare_group_fit` scaled 1.032x):

| Figure | element | native pt | placed pt |
|---|---|---|---|
| Fig. 2 (`severity_imdb.pdf`) | beta annotations | 5.5 | **5.3** |
| | legend | 6.5 | **6.3** |
| | tick labels | 7.0 | 6.8 |
| | x-axis labels | 7.5 | 7.2 |
| | panel titles | 8.0 | 7.7 |
| | y-axis label | 9.0 | 8.7 |
| Fig. 3 (`rare_group_fit.pdf`) | beta annotations | 5.25-6.0 | **5.4-6.2** |
| | legend | 6.5 | **6.7** |
| | tick labels / two-line x ticks | 7.0 | 7.2 |
| | x-axis label | 7.5 | 7.7 |
| | panel titles | 8.0 | 8.3 |
| Fig. 1 (TikZ, `main.tex` lines 262, 263, 265) | node text and p/q labels | `\scriptsize` = **7.0** | 7.0 |

The kit's 9 pt rule is enforced strictly only for body text and captions by CMS; in-figure text at 7-8 pt is routine in accepted ICASSP papers, but 5.3 pt beta annotations and 6.3 pt legends will be hard to read in print and a reviewer may say so. Captions themselves are 9 pt (PASS).

Edit: regenerate both figures with matplotlib `legend fontsize >= 7.5`, annotation `fontsize >= 7`, tick labels `>= 7.5`, so the placed sizes land at 7-8 pt (the 9 pt letter of the rule would need 9.3 pt native, which will not fit the legends; 7.5-8 pt is the defensible compromise). For Fig. 1 change `font=\scriptsize` to `font=\footnotesize` (8 pt) on `main.tex` lines 262, 263, 265 and widen `minimum width` of the `atm` style from 13mm to 15mm so `$A_4=\{1,2,4\}$` still fits.

### B2. Funding footnote is 8 pt (template: footnotes "Times 9-point type")
Page 1 footnote `This work is supported by NSF under Grant 2242215.` renders at 8.0 pt (measured). Cause: `\ninept` redefines `\normalsize` but leaves `\footnotesize` at the 10pt-article value of 8 pt, so every `\ninept` paper has this. Nobody has been rejected for it, but it is a one-token fix.

Edit: `main.tex` line 50, change `\thanks{This work is supported by NSF under Grant 2242215.}` to `\thanks{\small This work is supported by NSF under Grant 2242215.}` (`\small` is 9 pt under the article class).

### B3. Reference numbering order (kit: "numbered in alphabetic order or in order of appearance")
The manual `thebibliography` is in neither order. First-page citations appear as `[1, 2, 3, 34]`, then `[4, 5]`, `[6]`, `[11, 12, 13]`, `[3, 2, 28]`, `[16, 17]`, `[7, 8, 9]`. Entries 34, 28, 16, 17 are cited before 7.

Edit: reorder the `\bibitem` blocks in `main.tex` (lines 650-817) into first-citation order, or move to `\bibliographystyle{IEEEbib}` + a `.bib` file (IEEEbib is unsorted = order of appearance, and it is what the kit ships). If reordering by hand, the order of first citation is: buolamwini, hashimoto, sagawa, yang2021dir, mohri, li2020fair, rahimi2025fedavot, agarwal, cotter, chamon2020pacc, levy2020large, rizk, katharopoulos, rahimi2025agnostic, wang2020objective, cho2022biased, villani, peyre, sinkhorn, cuturi, csiszar, gietl, rockafellar, rahimi2026exactpenalty, uci_adult, rothe.

### B4. Submission-time actions stated by the kit (cannot be verified in the PDF)
- Filename must be the first author's last name: submit as **`Rahimi.pdf`**, not `main_fit.pdf`.
- Every author needs an ORCiD entered at submission (4 authors: Rahimi, Sodhi, Goyal, Kalogerias); papers with missing ORCiDs are auto-withdrawn.
- Author order in the form must match the PDF exactly: Rahimi, Sodhi, Goyal, Kalogerias.
- Abstract typed into the form must be identical to the PDF abstract.

---

## 2. SOFT fails (conventions; a reviewer might mention them)

### S1. Ten references are never cited in the text
`mcmahan2017fedavg` [10], `chamon2023nonconvex` [14], `hall1935` [23], `fordfulkerson1956` [24], `curi2020adaptive` [27], `namkoong2017variance` [29], `nemirovski2009` [30], `li2020fedprox` [31], `karimireddy2020scaffold` [32], `theodoropoulos2024restricted` [36]. With a manual bibliography they still print, so the list has 36 entries of which 26 are cited (the 27th "key" the checker found is the `%`-continued `hashimoto` line, which is fine). IEEE convention is that every listed reference is cited. Hall [23] and Ford-Fulkerson [24] were clearly meant to back Thm. 3 ("settled by flow duality"), Nemirovski [30] the rate, McMahan [10] FedAvg.

Edit (pick one per entry): cite them where they belong, e.g. `main.tex` line 300 `settled by flow duality \cite{hall1935,fordfulkerson1956} (proofs omitted for space)`; line ~130 `\textsf{FedAvg} \cite{mcmahan2017fedavg} optimizes a surrogate`; Thm. 7 proof sketch or line 397 `\cite{nemirovski2009}`; otherwise delete the `\bibitem`. Deleting all ten frees ~25 lines on page 5 and does not affect the page budget either way.

### S2. Reference [15] is a "submitted" manuscript with an open `%%FILLIN`
`main.tex` lines 720-723: `H.~Rahimi, S.~Pougkakiotis, and D.~Kalogerias, "An exact penalty method for constrained statistical learning over universal RKHSs," 2026, submitted.` followed by `%%FILLIN: replace with the arXiv number once posted.` The rendered entry reads `2026, submitted.` with no venue.

Edit: IEEE form is `..., submitted for publication, 2026.` or, once posted, `arXiv preprint arXiv:26xx.xxxxx, 2026.` Then delete the `%%FILLIN` comment (line 723) and the stale header comments at lines 6-11 (`Replace the local stand-in spconf.sty with the official ICASSP one before submitting` is no longer true; the markers legend can go too).

### S3. Fig. 3 right panel: the legend covers the data
In `rare_group_fit.pdf` (IMDb-Wiki panel) the three-row legend sits at upper-left and the blue and orange curves for beta in {0.5, 1, 1.5} run straight through the legend text; the `beta=0.5` annotation is overprinted by "(uniform". In Fig. 2 right panel the legend's lower edge sits on the `beta=1` annotation and the tops of the beta=1 markers (borderline). Legend labels are also unnecessarily long ("group-blind average (uniform over the observed groups)", "full coverage (every group every step, weighted by p)"), which is what forces the overlap.

Edit: regenerate with `loc='lower right'` for the IMDb panel (empty region under the curves at x > 60), or put one shared legend above/below the two panels (`fig.legend(..., ncol=3, loc='upper center')`) and shorten labels to `GAVOT`, `group-blind avg.`, `full` (the caption already defines them). Same for Fig. 2 right: `loc='lower right'`.

### S4. Acronyms not defined at first use
- `SGD` is never expanded in the body (the title and keywords spell it out, the abstract and Sec. 1 do not). Edit: `main.tex` line 61, `Minibatch stochastic gradient descent (SGD) is group-blind:`.
- `CVaR` is used in the abstract (line 73) and contribution 3 (line 151) before its definition at eq. (10). Edit: line 73, `A mean--conditional-value-at-risk (CVaR) layer`.
- `MSE` appears only in Table 1/Fig. 2/Fig. 3 labels, never defined; `KL` (line 401, "KL-closest") never expanded. Edit: line 484, `linear regression (mean-squared error, MSE) on $128$-d face embeddings`; line 401, `is Kullback--Leibler (KL) closest`.

### S5. Numeric formatting is inconsistent (leading zeros)
Table 1 writes `0.2269`, `0.2479`; Table 2, the protocol paragraph and E2/E3 write `.31`, `.60`, `.073`, `.119`, `.0210`. IEEE style uses the leading zero. Edit: add `0` in Table 2 column nu (`$.31$` -> `$0.31$` etc., lines 582-587), in lines 487-491 (`\nu{=}.60`, `.31`, `.88`), and in E2/E3 (lines 553-560, 596-598).

### S6. Cross-reference abbreviations mixed
`Thm.~\ref{thm:feas}` (Fig. 1 caption, line 294; contributions line 145 `Thm.~\ref{thm:infeasible}`) versus `Theorem~\ref{thm:rate}` elsewhere; `Cor.~` at line 145 versus no other corollary reference. Edit: pick one form; IEEE convention is the full word in running text (`Theorem 3`, `Corollary 4`) and the abbreviation only inside parentheses.

### S7. Last-page column balance (template: "arrange the columns so that they are evenly balanced")
Page 5 left column is full ([1]-[17]) and the right column stops at about 78% ([18]-[36]). Minor, and it will change anyway if S1 deletes entries. Edit if desired: `\usepackage{balance}` and `\balance` before `\begin{thebibliography}`, or insert `\vfill\pagebreak` between entries [18] and [19] after the final edit.

---

## 3. Other things a reviewer might notice (informational, no rule)

- Page 3 begins with a two-line widow: the last sentence of Theorem 7, "The constant is that of full-participation SGD, independent of batch coverage.", is stranded at the top of the left column, separated from the theorem statement on page 2. Consider folding it into the paragraph after the theorem or letting the theorem end at eq. (8).
- Fig. 2 and Fig. 3 are first referenced on page 3 (E2, E3) and appear on page 4 (normal for `figure*` floats; fine).
- Fig. 3 panels have no y-axis labels; the unit is only in the panel title ("(cross-entropy)", "(MSE)"). Acceptable, but an `ylabel` costs nothing.
- Reference [10]: `B.~A. y~Arcas` should be `B. Agüera y Arcas`. Reference [34] (Yang et al., ICML 2021) and [36] (Theodoropoulos et al., ICASSP 2024) lack page numbers while every other ICML/ICASSP entry has them (ICML 2021 is PMLR 139, pp. 11842-11851; ICASSP 2024 pp. 6260-6264 -- verify). [33] UCI Adult would normally carry `[Online]. Available: https://doi.org/10.24432/C5XW20`.
- `\renewcommand{\refname}{REFERENCES}` (line 646) is redundant: `spconf.sty` already typesets the heading via `\section{References}` in caps. Harmless.
- `\pagestyle{empty}\thispagestyle{empty}` (line 58) is redundant with the style file; harmless.
- `\usepackage{url}` is loaded but never used; `hyperref` (which the template loads) is not loaded, so nothing is clickable. Not a rule.
- Algorithm 1 line numbers render at 8 pt (`algorithmic` uses `\footnotesize` for them); the algorithm body is 9 pt. Same class as B2, inherent to the package.
- The `figure` for Fig. 1 uses `[t]` and lands at the top of page 2 right column; Table 1 at top of page 3 right; Figs. 2-3 at top of page 4; Table 2 directly under them in the left column. All consistent with "top of columns" preference.
- Keywords line ends with a period; the template example has none. Either is accepted.
- Title is split with `\\`; the style file uppercases it and sets it `\large\bf` (12 pt bold), which is what every spconf paper gets even though the template prose says 14 pt. Style-governed, PASS.

---

## 4. Full checklist

Legend: HARD = stated by kit/template/style, SOFT = convention. Measurements are from the PDF, not the source, unless noted.

| # | Rule | Level | Paper | Grade |
|---|---|---|---|---|
| 1 | Max 5 pages; 4 pages technical content | HARD | 5 pages; pages 1-4 content, page 5 references only | PASS |
| 2 | Page 5 only references / funding ack / ethics statement | HARD | Page 5 = "7. REFERENCES" [1]-[36], nothing else; funding is a page-1 footnote (allowed) | PASS |
| 3 | Letter (216x279 mm) or A4 | HARD | All 5 pages 612x792 pt = 215.9x279.4 mm (US Letter) | PASS |
| 4 | Print area 178x229 mm | HARD | `spconf.sty`: `\textwidth 178truemm`, `\textheight 229truemm`; text x from 19.2 mm to 196.4 mm; both spanning figures at `width=\textwidth` = 178 mm | PASS |
| 5 | Left margin 19 mm | HARD | Leftmost text at 19.2 mm on every page | PASS |
| 6 | Top margin 25 mm (35 mm title page) | HARD | Pages 2-5 first baseline 28.0-28.9 mm from top (inside); title baseline 36.4 mm | PASS |
| 7 | Two columns 86 mm, 6 mm gap, fully justified | HARD | Style `\twocolumn`, `\columnsep 6truemm`; (178-6)/2 = 86 mm; LaTeX justification | PASS |
| 8 | Top 50 mm of page 1 reserved for title/authors | HARD | ABSTRACT heading baseline at 82.4 mm from top | PASS |
| 9 | Times-Roman (or CM) | HARD | NimbusRomNo9L (Times clone) body; CM/AMS math; Helvetica clone for `\textsf{GAVOT}`; DejaVu Sans inside figures | PASS |
| 10 | Font >= 9 pt throughout incl. captions | HARD | Body, captions, tables, references all 9.0 pt (`\ninept`); sub/superscripts 5-7 pt (inherent); footnote 8 pt (B2); in-figure text 5.3-8.7 pt (B1); Fig. 1 TikZ 7 pt (B1) | BORDERLINE |
| 11 | <= 8 lines/inch (3.2 lines/cm) at 9 pt | HARD | Baseline step 10.4 pt = 6.92 lines/inch on pages 3 and 5 | PASS |
| 12 | Not double-spaced | HARD | Single-spaced, `\baselinestretch .95` via `\ninept` | PASS |
| 13 | Title: bold, ALL CAPS, no math, Unicode-representable, no uncommon acronym | HARD | `GROUP-FAIR STOCHASTIC GRADIENT DESCENT VIA MASKED OPTIMAL TRANSPORT`, bold, caps in source and via style, no `$`, no acronym | PASS |
| 14 | Title begins ~35 mm from top, centered | HARD | Baseline 36.4 mm, centered by style | PASS |
| 15 | Author names + affiliations below title, mixed case; NOT blind | HARD | Four names (italic per style), department, university, city, emails | PASS |
| 16 | Author order matches submission form; every author has ORCiD | HARD | Cannot verify from PDF; action at submission (B4) | ACTION |
| 17 | Abstract 100-150 words, top of left column, <= 80 mm tall | HARD | 151 words (counted with macros collapsed); block 62.3 mm tall; starts left column | PASS (151 ~ 150) |
| 18 | 12 mm gap after abstract before main text | SOFT (template) | Index Terms to "1. INTRODUCTION" = 12.4 mm | PASS |
| 19 | Index Terms line, up to 5 keywords | HARD | `Index Terms---` line via `keywords` env; 5 keywords | PASS |
| 20 | Section headings numbered, caps, bold, centered, period after number | HARD (style) | "1. INTRODUCTION" ... "7. REFERENCES", all via `spconf.sty` | PASS |
| 21 | Subsection style (bold, sentence case, flush left); sub-subsections discouraged | HARD | No `\subsection` used; run-in bold paragraph heads instead | PASS (n/a) |
| 22 | First paragraph of a section unindented, later ones indented | SOFT (template) | Every paragraph is `\noindent\textbf{...}` run-in, so none indented; consistent house style | PASS (n/a) |
| 23 | No page numbers | HARD | `\pagestyle{empty}` (style + explicit); no numerals at page foot in extracted text | PASS |
| 24 | References numbered, cited as [n] | HARD | 36 numbered entries; in-text `[1, 2, 3, 34]` bracket style | PASS |
| 25 | References in alphabetic OR first-appearance order | HARD | Neither (B3) | BORDERLINE |
| 26 | IEEE citation style (abbrev. venues, vol./no./pp.) | HARD (kit link) | Consistent abbreviations (`Proc. Int. Conf. Machine Learning (ICML)`, `Adv. Neural Inf. Process. Syst. (NeurIPS)`, `Proc. IEEE Int. Conf. Acoustics, Speech and Signal Processing (ICASSP)`); page ranges with en-dash; missing pages on [34], [36]; "submitted" entry [15] (S2) | PASS with S2 |
| 27 | All listed references cited | SOFT | 10 uncited (S1) | FAIL |
| 28 | References not truncated / no placeholder text | SOFT | No "et al." truncation; `%%FILLIN` comment only in source (S2) | PASS |
| 29 | Relation to prior work discussed | HARD (template) | "Other algorithms" paragraph in Sec. 1 plus contributions; FedAVOT, agnostic FedAvg, DRO, reductions, importance sampling | PASS |
| 30 | Illustrations within margins; may span columns | HARD | Figs. 2-3 exactly `\textwidth`; Fig. 1, Tables, Algorithm within column | PASS |
| 31 | Illustrations at top of columns preferred | SOFT (template "if possible") | All floats `[t]`; all render at column/page tops | PASS |
| 32 | Every illustration captioned and numbered | HARD | Fig. 1-3, Table 1-2, Algorithm 1 | PASS |
| 33 | Figure captions below, table captions above | SOFT (IEEE) | Figures: caption after graphic; Tables: `\caption` before `tabular`; Algorithm: caption on top | PASS |
| 34 | Black-and-white legible | HARD | Blue circle / orange square / red triangle with solid vs dashed; Fig. 1 rare edge is thicker (0.7 pt vs 0.35 pt) as well as red | PASS |
| 35 | Legend does not obscure data | SOFT | Fig. 3 right panel overlaps (S3); Fig. 2 right borderline | FAIL |
| 36 | Footnotes sparse, bottom of column, 9 pt | HARD (template) | One footnote (funding), bottom of page-1 left column, 8 pt (B2) | BORDERLINE |
| 37 | PDF, no security, first-page-first | HARD | `is_encrypted=False`; 5 pages in order | PASS |
| 38 | All fonts embedded and subset; no Type 3 | HARD | 33 fonts, all embedded, all subset-prefixed; Type1 (Nimbus, CM, AMS) + CIDFontType2 (DejaVu from matplotlib); zero Type 3 | PASS |
| 39 | File <= 5 MB | HARD | 439,938 bytes | PASS |
| 40 | Filename = first author's last name | HARD | Current `main_fit.pdf`; submit as `Rahimi.pdf` (B4) | ACTION |
| 41 | Copyright form (post-acceptance) | HARD | n/a at submission | n/a |
| 42 | Compliance with Ethical Standards statement (optional, page 5 only) | SOFT | None present; not required | PASS (n/a) |
| 43 | `\ninept` optional 9 pt | SOFT | Used (line 56) | PASS |
| 44 | Equations numbered and referenced with `\eqref` | SOFT | (1)-(11) numbered; all references via `\eqref` | PASS |
| 45 | Acronyms defined at first use | SOFT | SGD, CVaR (before Sec. 4), MSE, KL undefined (S4); MOT, LDS defined | FAIL |
| 46 | En-dash for ranges/compounds, em-dash sparingly | SOFT | `mean--CVaR`, `Rockafellar--Uryasev`, `supply--demand`, `pp. 77--91`; no em-dashes in body | PASS |
| 47 | Consistent number formatting | SOFT | Leading zeros mixed (S5) | FAIL |
| 48 | Consistent cross-reference abbreviations | SOFT | `Thm.`/`Theorem`, `Cor.` mixed (S6) | FAIL |
| 49 | No orphan headings at column bottoms | SOFT | None: every `\section` heading has text beneath it on the same column | PASS |
| 50 | No widow lines from split theorem/paragraph | SOFT | Theorem 7's last sentence alone at top of page 3 (Sec. 3 note) | BORDERLINE |
| 51 | Balanced columns on the last page | SOFT (template) | Page 5 right column ~78% (S7) | FAIL (minor) |
| 52 | Tables >= 9 pt, booktabs, no vertical rules | SOFT | Table 1 `\small` = 9 pt under `\ninept`; Table 2 9 pt; booktabs | PASS |
| 53 | Units and quantities | SOFT | `(%)`, `(MSE)`, `128-d`, `4000 steps`, `5 seeds` consistent | PASS |
| 54 | No leftover placeholders / TODO / FILLIN rendered | SOFT | Nothing rendered; one `%%FILLIN` comment and stale header comment in source (S2) | PASS (source hygiene) |
| 55 | Style file is the official one | HARD | `diff spconf.sty kit/spconf.sty` = identical | PASS |
| 56 | Manuscript in English, black ink text | HARD | Yes | PASS |
