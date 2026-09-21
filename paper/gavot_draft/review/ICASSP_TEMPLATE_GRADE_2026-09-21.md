# ICASSP 2027 template grade, second pass: rendered Template.pdf vs our main_fit.pdf (2026-09-21)

Materials compared
- Reference: `paper/gavot_draft/kit/Template.pdf` (3 pages, rendered 2026-08-31 with the same MiKTeX pdfTeX 1.40.28 as ours), `kit/Template.tex`, `kit/spconf.sty` (byte-identical to the `spconf.sty` we compile with), kit page `cmsworkshops.com/ICASSP2027/papers/paper_kit.php`.
- Ours: `paper/gavot_draft/pdf/main_fit.pdf` (5 pages, 423,315 bytes, compiled 2026-09-21 11:59), source `paper/gavot_draft/overleaf/main.tex`.
- Method: both PDFs rendered at 100/200/220 dpi and inspected side by side; positioned text extracted with `mgs -sDEVICE=txtwrite -dTextFormat=0` (font name, size, baseline y for every span); page boxes and font embedding via pypdf (recursing into figure XObjects); word counts with python over the source with macros collapsed (`\textsf{FedAVOT}` = 1 word, each `$...$` = 1 word, hyphenated compounds = 1 word), which is also what a whitespace count gives (155 both ways).
- Previous grade `review/ICASSP_GRADE_2026-09-21.md`: every applied fix was re-verified in the PDF (see section 5).

## Summary: 2 must-fix, 9 should-fix, 38 fine

The layout is the template's own to the millimetre (same style file, same title/author/abstract geometry, same 12 pt title, same 9 pt captions, same footnote placement, references in first-appearance order, page 5 references only). The two things that miss a stated rule are the abstract length (155 words against "about 100 to 150") and an undefined symbol (`m/K`, `m` never introduced). Everything else is presentation: sub-9 pt text inside the two matplotlib figures, two colliding annotations in Fig. 3, a wrapped algorithm line, and the last-page column balance.

---

## 1. Must-fix

### M1. Abstract is 155 words; template: "about 100 to 150 words"
Measured: 155 words (source, macros collapsed; whitespace count also 155), 20 typeset lines, 55.4 mm from first to last body baseline, 66.3 mm from the ABSTRACT heading to the Index Terms baseline (limit 80 mm: PASS on height), 12.3 mm from Index Terms to "1. INTRODUCTION" (template asks 12 mm; the template's own render has 10.2 mm: PASS). The previous grade counted 151; the CVaR expansion added four. Only the word count is over.

Proposed replacement, **136 words** (whitespace count and macro-collapsed count agree), same claims, same macros, drop-in for `main.tex` lines 61-77 (`\begin{abstract}` ... `\end{abstract}`):

```latex
\begin{abstract}
Minibatch stochastic gradient descent (SGD) is group-blind: a batch contains
each group in proportion to its prevalence, not to its weight in the
objective, so SGD optimizes a prevalence-weighted surrogate. Reading a
minibatch as a partial-participation event over groups, we carry the masked
optimal transport construction of \textsf{FedAVOT} across: aligning the
batch-composition law $q$ with the target importance $p$ yields per-batch
group weights whose stochastic subgradient is exactly unbiased, at the
$O(1/\sqrt{T})$ rate. Alignment is feasible under a Hall-type condition;
past it, Sinkhorn returns an information projection with closed-form
residual, splitting the excess risk into an instance-fixed alignment gain
and an optimization residual paid by the estimator. A sweep over eleven
availability skews on Adult and IMDb-Wiki shows the two crossing where the
decomposition predicts. A mean--conditional-value-at-risk (CVaR) layer
reaches the worst group at rate $O(\kappa(\alpha,\gamma)/\sqrt{T})$.
\end{abstract}
```

What changed and why: "which groups appear in a batch is decided by their prevalence in the data, not by how much they are meant to count in the objective" -> "a batch contains each group in proportion to its prevalence, not to its weight in the objective" (same statement, 11 words shorter); "A minibatch is a partial-participation event over groups, so we carry" -> "Reading a minibatch as a partial-participation event over groups, we carry"; "whose residual we compute in closed form" -> "with closed-form residual"; "an alignment gain fixed by the instance" -> "an instance-fixed alignment gain" (the paper's own phrase, p. 1); "on top" dropped. Every claim (group-blindness, surrogate, FedAVOT transfer, exact unbiasedness at O(1/sqrt T), Hall-type feasibility, information projection, closed-form residual, gain/residual split, eleven skews, crossover, CVaR rate) is kept. Remember the kit rule that the abstract typed into the submission form must be identical to this text.

### M2. `m/K` uses a symbol `m` that is never defined
`main.tex` line 499 (protocol paragraph) and line 510 (Table 1 caption) write "the fixed multiplier $m/K$"; nowhere in the paper is `m` introduced (the paper's symbols are `N` groups, `K` observed per step, `b` batch size; `m(\cdot;\theta)` is the predictor, which makes `m/K` actively misleading). FedAVOT's multiplier is `N/K`.

Edits:
- line 498-499: `the \emph{fixed multiplier} $m/K$;` -> `the \emph{fixed multiplier}, weights $(N/K)\,p_i$ on the observed groups \cite{rahimi2025fedavot};`
- line 510: `The fixed multiplier $m/K$ reaches` -> `The fixed multiplier $(N/K)\,p_i$ reaches`
(Both lines stay within their current line count; the caption grows by ~4 characters.)

---

## 2. Should-fix

### S1. Text inside Figs. 2-3 is 6.7-8.7 pt (kit: "no smaller than nine point type throughout the paper, including figure captions")
Both figures were regenerated since the first grade (native width now 185.1 mm and 184.2 mm, placed at 178 mm = scale 0.962/0.966) but the placed sizes are still below the 7.5-8 pt compromise the first grade asked for. Measured in the PDF (DejaVu Sans, placed size):

| element | size |
|---|---|
| y-axis label "overall loss F_p (MSE)" | 8.7 pt |
| panel titles | 8.2 pt |
| x-axis labels, "cross-entropy", "MSE" | 7.7 pt |
| legend entries, Fig. 3 two-line tick labels | 7.2 pt |
| tick numbers, beta annotations | 6.7-6.8 pt |
| subscripts in eta_t, F_p | 5.4-6.1 pt |

Captions are 9 pt (PASS). Fig. 1 (TikZ) is now `\footnotesize` = 8 pt (previous B1 applied). Fix: in the plotting script set `tick labelsize=8`, `legend fontsize=8`, annotation `fontsize=8`, axis label 8.5, title 9, and export at exactly 178 mm wide (`figsize=(7.0, ...)`) so the placed size equals the native size.

### S2. Fig. 3 right panel: the "beta=3" annotation collides with the panel title "(MSE)", and "beta=1.5"/"beta=2" overprint each other
Visible at 220 dpi: "IMDb-Wiki: top-importance identities (MSE)beta=3" and "beta=1.5beta=2". In Fig. 2 (both panels) the beta=1.5/beta=2 labels touch but remain readable. Fix: offset the last three annotations (`xytext` alternating above/below the marker, or `ha='right'` for beta=3) and add `pad` to the title. Legends no longer cover data anywhere (previous S3 applied).

### S3. Underbrace labels in eq. (9) are 6 pt italic
Page 3, y=337 pt: "alignment floor" / "optimization residual" render at 5.98 pt (script-style `\text`). Edit `main.tex` lines 407-408: `\underbrace{\Phi(\hat p)-\Phi(p)}_{\text{alignment floor}}` -> `\underbrace{\Phi(\hat p)-\Phi(p)}_{\textnormal{\small alignment floor}}` and likewise `_{\textnormal{\small optimization residual}}` (`\small` = 9 pt under `\ninept`). Check the column width afterwards; if the labels collide, use `\mathclap{}` from `mathtools`.

### S4. Algorithm 1, line 8 wraps onto a second line
The `t^t` update spills "t^{t-1}\})" onto a continuation line (page 2, right column). Edit `main.tex` line 354: break it deliberately, e.g. define `\State $\delta^t \leftarrow 1-\tfrac{1}{\alpha}\sum_{i\in A^t}Y[i,j(t)]\mathbf{1}\{\hat f^t_i>t^{t-1}\}$` as line 8 and `\State $t^{t}\leftarrow t^{t-1}-\eta(1-\gamma)\,\delta^t$` as line 9 (the text refers to "lines 6 and 8", so update line 450 to "lines 6, 8 and 9"), or shrink with `\textstyle`.

### S5. Table 1 column head "unif. avg" names the method differently from everywhere else
Text, Fig. 2, Fig. 3 and Table 2 say "group-blind avg."/"group-blind averaging". Edit `main.tex` line 516: `unif.\ avg` -> `blind avg.` (fits the column at `\tabcolsep 3pt`).

### S6. Last page: columns unbalanced (template: "arrange the columns so that they are evenly balanced if possible")
Page 5 left column ends at 254.4 mm (full), right column at 223.7 mm, i.e. 86% of the column (was 78%; improved by the reorder). Edit: `\usepackage{balance}` in the preamble and `\balance` immediately before `\begin{thebibliography}` (line 653), or move `\vfill\pagebreak` (the template's own device) to after entry [17].

### S7. Reference [33] has no page numbers; [7] could now have them
`theodoropoulos2024restricted` (ICASSP 2024) is the only conference entry without `pp.`; every other ICASSP/ICML entry has them. Add the pages (ICASSP 2024 proceedings; verify against IEEE Xplore). `rahimi2025fedavot` (ICASSP 2026, held April 2026) can also carry pages if the proceedings are out.

### S8. Source hygiene in the Overleaf file
`main.tex` lines 6-11 still say "Replace the local stand-in spconf.sty with the official ICASSP one before submitting" (no longer true) and list the `%%FILLIN`/`%%CHECK` marker legend; line 814 still has `%%FILLIN: replace with the arXiv number once posted.` under the (now correctly formatted) submitted entry. Delete lines 6-11 and 814. Nothing renders, but a reviewer with source access, or the next person to edit, will trip on them.

### S9. Email lines are 12 pt monospace (optional)
The style sets the whole author block in `\large` (12 pt), and `\texttt` at 12 pt makes the two e-mail lines the visually heaviest thing on the page (see the 200 dpi render). The template's example puts "optional e-mail address" in the address block in the same Times face. Edit `main.tex` lines 53-54: `\texttt{\{herlock.rahimi, dionysis.kalogerias\}@yale.edu}` -> `{\normalsize\texttt{\{herlock.rahimi, dionysis.kalogerias\}@yale.edu}}` (same for the gmail line), or drop `\texttt` altogether. Cosmetic; many accepted ICASSP papers do what we do.

---

## 3. Fine (verified against the template)

See the table in section 4; the notable confirmations: the funding footnote is now 9.0 pt (template prose says 9 pt; the template's own footnote actually renders at 8 pt, so we are stricter than the template); references are in exact first-appearance order and all 36 are cited; no `??`, no `FILLIN`, no doubled words, no unmatched brackets in the rendered text (the (80 vs 78) / (23 vs 24) parenthesis counts on pages 3-4 are text-extraction artefacts of `\big(` delimiters and axis labels, checked visually); Theorem 7 no longer splits across pages 2-3; 30 fonts, all embedded and subset, no Type 3.

---

## 4. Comparison table, template vs ours

Measurements are from the PDFs (mm from the top/left page edge, sizes from the font dictionaries).

| # | Element | Template says / does | Ours | Grade |
|---|---|---|---|---|
| 1 | Abstract word count | "about 100 to 150 words" (its own abstract: about 90) | 155 | **MUST-FIX (M1)** |
| 2 | Abstract height | "no more than 3.125 inches (80 mm) in length" (its own: 42.0 mm heading to Index Terms) | 66.3 mm heading to Index Terms; 55.4 mm body | PASS |
| 3 | Abstract placement | top of left column, "about 0.5 inch (12 mm) below the title area" (its own: 13.8 mm below last affiliation baseline) | 13.1 mm below the last address baseline | PASS |
| 4 | Gap abstract -> main text | "Leave a 0.5 inch (12 mm) space" (its own: 10.2 mm baseline to baseline) | 12.3 mm | PASS |
| 5 | Abstract identical to form text | required | action at submission (use the M1 text in both) | ACTION |
| 6 | Title position | "begin 1.38 inches (35 mm) from the top edge" (its own baseline 37.4 mm, cap top ~34.5 mm) | baseline 36.3 mm, second line 40.9 mm | PASS |
| 7 | Title font | "Times 14-point, boldface", "completely capitalized" (its own render: NimbusRomNo9L-Medi 12.0 pt via `\large\bf`, uppercase) | NimbusRomNo9L-Medi 12.0 pt bold, uppercase, centered, two lines | PASS (identical to template render) |
| 8 | Author line | "capital and lower case letters"; style sets `\em` (italic 12 pt) | four names italic 12 pt on one line, `\quad`-separated | PASS |
| 9 | Affiliation lines | "may require two or more lines"; style centers a tabular | 1 affiliation line + 2 e-mail lines, centered, 12 pt | PASS (S9 cosmetic) |
| 10 | 50 mm reserved band / top of page 1 | title block occupies 37-58 mm in template | ours 36-69 mm; abstract heading at 82.2 mm (template 71.3 mm) | PASS |
| 11 | Not blind | "include the authors' names on the PDF" | names present | PASS |
| 12 | Index Terms | `\keywords` -> bold-italic "Index Terms---" then keywords; "up to 5 keywords" (its example has no final period) | "Index Terms--- Group fairness, optimal transport, stochastic gradient descent, distribution shift, conditional value at risk." (5 keywords, trailing period) | PASS |
| 13 | Major headings | "all capital letters, bold face, centered, one blank line before and after, period after the number not a colon" | "1. INTRODUCTION" ... "7. REFERENCES", all via the same `\@sect` | PASS |
| 14 | Subheadings | "lower case (initial word capitalized) in boldface, start at the left margin on a separate line" (5.1. Subheadings) | none; unnumbered bold run-in heads ("Instances and protocol.") | PASS: the template does not forbid run-in heads and does not require subsections; run-in bold heads are the norm in 4-page ICASSP papers. Converting ~20 heads to `\subsection` would cost ~20 lines |
| 15 | Sub-subheadings | "discouraged" | none | PASS |
| 16 | First-paragraph indentation | "first paragraph in each section should not be indented, all following paragraphs indented" | headed paragraphs are `\noindent` by construction; unheaded follow-on paragraphs (e.g. "Both gamma=1 and alpha=1 recover...", p. 3) are indented; section openers ("Exact alignment delivers...", Sec. 4; Conclusion) are not | PASS (consistent with the rule wherever it applies) |
| 17 | Figure captions | below the figure, "**Fig. 1**. Example of ..." (style: bold "Fig. N" + "." + text) | Fig. 1-3 captions below, "**Fig. 2**. IMDb-Wiki severity sweep: ..." | PASS |
| 18 | Table captions | IEEE: above the table; style: bold "Table N." | Table 1, 2 captions above | PASS |
| 19 | Algorithm | (not in template) | "Algorithm 1 GAVOT: ..." caption above, ruled; line 8 wraps | S4 |
| 20 | Figure placement | "at the top of columns"; "may span the two columns"; "within the designated margins" | Fig. 1 top of p. 2 right; Table 1 top of p. 3 right; Figs. 2-3 `figure*` at top of p. 4, exactly `\textwidth` = 178 mm; Table 2 below them | PASS |
| 21 | B/W legibility | "readable when printed on a black-only printer" | grayscale render checked: circle/square/triangle markers and solid/dashed styles separate the three rules; GAVOT and full both dark but distinguished by marker and position | PASS |
| 22 | Figure text size | "no smaller than nine point ... including figure captions" | captions 9 pt; in-figure 6.7-8.7 pt; Fig. 1 TikZ 8 pt | S1 |
| 23 | Annotation collisions | n/a | Fig. 3 right: beta=3 into the title, beta=1.5/beta=2 overlap | S2 |
| 24 | Equations | numbered, referenced with `\eqref` | (1)-(11) at right margin, referenced as (n) | PASS |
| 25 | Footnotes | "sparingly (or not at all!)", bottom of the column, "Times 9-point" (template's own renders at 8 pt) | one funding footnote, bottom of p. 1 left, 9.0 pt (B2 applied) | PASS |
| 26 | Funding acknowledgement | template: `\thanks` footnote on page 1 (page 5 also allowed by kit) | same as template | PASS |
| 27 | Copyright notice | `\copyrightnotice` only for the preprint option; none in the rendered template; form is submitted separately | none | PASS (n/a) |
| 28 | Compliance with Ethical Standards | optional, page 5 only | none | PASS (optional; public datasets, no new human-subject data) |
| 29 | Relation to prior work | "must be present" | "Other algorithms" paragraph + contributions, Sec. 1 | PASS |
| 30 | References heading and numbering | "List and number all ... alphabetic order or in order of appearance", cite as "[2]" | 36 entries, exact first-appearance order, bracket citations `[1, 2, 3, 4]` | PASS (B3 applied) |
| 31 | Reference style | example: `A.B. Smith, C.D. Jones, and E.F. Roberts, "Article title," Journal, vol. 62, pp. 291--294, January 1920.` / `in Proceedings Title. IEEE, 2003, vol. II, pp. 803--806.` | `P. Hall, "On representatives of subsets," J. London Math. Soc., vol. 10, no. 1, pp. 26--30, 1935.`; `in Proc. Int. Conf. Machine Learning (ICML), 2018, pp. 1929--1938.`; en-dash ranges throughout; `[Online]. Available:` for UCI; `submitted for publication, 2026.` for [34] | PASS; [33] lacks pages (S7) |
| 32 | All references cited | convention | 36/36 cited, 0 uncited (S1 of previous grade applied) | PASS |
| 33 | Page 5 content | "only references to the prior literature" (kit: + funding ack + ethics statement) | "7. REFERENCES" [1]-[36] only | PASS |
| 34 | Last-page balance | "evenly balanced if possible" (`\vfill\pagebreak`) | left 100%, right 86% | S6 |
| 35 | Page count | 5 max, 4 technical | 5; technical content ends on p. 4 | PASS |
| 36 | Page size | Letter 216 x 279 mm (A4 allowed) | all 5 pages 612 x 792 pt = 215.9 x 279.4 mm | PASS |
| 37 | Print area / margins | 178 x 229 mm; left 19 mm; top 25 mm (35 mm title page) | text x = 19.1-197.3 mm; first baselines p. 2-5 at 28.2-28.9 mm; last baselines 254.4 mm (= 25 + 229) | PASS |
| 38 | Columns | 86 mm, 6 mm gutter, fully justified | style-set (178-6)/2 = 86 mm; justified | PASS |
| 39 | Font family | Times-Roman (or CM per kit) | NimbusRomNo9L (Times) body, CM/AMS math, NimbusSanL for `\textsf`, NimbusMonL for e-mails, DejaVu Sans in figures | PASS |
| 40 | Body size / spacing | >= 9 pt; <= 8 lines/inch | 9 pt body, captions, tables, references; 10.4 pt baseline step = 6.9 lines/inch | PASS |
| 41 | No page numbers | "do not paginate" | none (`\pagestyle{empty}`) | PASS |
| 42 | Fonts embedded | TrueType/Type 1 preferred | 30 fonts, all embedded and subset (Type1 + CIDFontType2), 0 Type 3 | PASS |
| 43 | File size | <= 5 MB | 423,315 bytes | PASS |
| 44 | Filename | first author's last name | submit as `Rahimi.pdf` | ACTION |
| 45 | ORCiD / author order | every author; order matches form | Rahimi, Sodhi, Goyal, Kalogerias | ACTION |
| 46 | Style file | official | `diff spconf.sty kit/spconf.sty` clean | PASS |
| 47 | Widows / split theorems | convention | Theorem 7 now entirely on p. 3 (previous note applied); no orphan headings | PASS |
| 48 | Acronyms | convention | SGD, CVaR (abstract), MOT, KL, MSE, LDS all expanded at first use | PASS |
| 49 | Leading zeros | IEEE | Table 2 `0.31`..., E2/E3 `0.073`, `0.0210` | PASS |
| 50 | Cross-reference words | IEEE | "Theorem 3", "Corollary 4", "Lemma 5"; only `\cite[Thm.~1]` abbreviated (inside a citation, fine) | PASS |
| 51 | Undefined symbol | n/a | `m/K` | **MUST-FIX (M2)** |
| 52 | Method naming | n/a | "unif. avg" (Table 1) vs "group-blind avg." (everywhere else) | S5 |
| 53 | Language sweep | n/a | no doubled words, no `??`, no `FILLIN`/`TODO` rendered, brackets balanced, no lowercase sentence starts (all "i.i.d." hits), hyphenation and quotes balanced (34/34) | PASS |
| 54 | Source hygiene | n/a | stale header comment (lines 6-11), `%%FILLIN` (line 814) | S8 |

## 5. Previous grade: which fixes landed (verified in the PDF)

| Item | Status |
|---|---|
| B1 in-figure text | Partly: Fig. 1 TikZ now 8 pt; Figs. 2-3 regenerated but still 6.7-8.7 pt placed (S1) |
| B2 footnote 9 pt | Done (measured 8.97 pt) |
| B3 reference order | Done (first-appearance order exact) |
| S1 uncited references | Done (0 uncited; Hall/Ford-Fulkerson cited at flow duality, Nemirovski at the bound, McMahan/FedProx/SCAFFOLD in Sec. 1, Theodoropoulos in Sec. 4) |
| S2 "submitted" entry | Done in the PDF ("submitted for publication, 2026."); `%%FILLIN` comment still in source (S8) |
| S3 legend over data | Done (Fig. 3 right legend removed; Fig. 2 legend only in the right panel, clear of the curves) |
| S4 acronyms | Done |
| S5 leading zeros | Done |
| S6 Thm./Cor. | Done |
| S7 column balance | Improved (78% -> 86%), still unbalanced (S6) |
| Theorem 7 widow | Done |
| [10] Agüera y Arcas, [4] pages, [35] DOI | Done; [33] pages still missing (S7) |
