# Changes applied to the working copy (fedavot-overleaf-v2-work/main.tex), 2026-09-15

Compiles to 4 pages + references on page 5 (pdflatex x2, stand-in spconf.sty).
Full unified diff: review/diff_vs_original.txt. PDF: review/GAVOT_draft_work.pdf.

## Section 2 (problem definition)
- S8: Prop. 1, "(a probability vector)" after the definition of p-tilde.
- S11: Contributions 1, "is agnostic FedAvg" -> "reduces, under uniform-within-batch averaging, to agnostic FedAvg".

## Section 3 (proposed approach)
- A17: "(p, r, E)" -> "(p, q, E)".
- A16: Thm. 10 brace label "<= DG/sqrt(T)" -> "optimization residual"; proof now states what Thm. 8 actually bounds and that eps_T also carries the p-vs-p-hat mismatch along the trajectory. HERLOCK SHOULD READ THIS ONE.
- A15: infeasible Sinkhorn sentence reworded without the KL argument order; Gietl & Reffel 2013 added to the bibliography and cited.
- A13: Lemma 7 proof wording (row-marginal identity, not "apply Lemma 6").

## Section 5 (experiments)
- I1/I5/I6/A11: Instances paragraph now names the models, step sizes, group sizes, the 85/10/3/1/1 split, the 100 identities (not "age tiers"), and the H=5 local steps before the weighted average.
- T1a: Table 1 Adult prevalence fixed multiplier "div." -> 0.670.
- E1b: "diverges on every instance" -> diverges on both aligned instances, far off on the other two.
- T2cap: Table 2 caption states the t convention (Welch, population std). His t values kept.
- E2d: added the two Adult skews where the gain exceeds the floor gap.
- F1: Fig. 2 regenerated as vector in his notation (nu, group-blind average, floor Phi); 0.92 column width.

## Cuts made to hold the page budget (all my additions or the two sentences named in the memo)
- E2 closing sentence shortened; E3 last two sentences removed (memo item 4).
- Dropped from my own additions: the Table 1 caption clause "and is far off when they are uniform" (E1 says it), the H=5 parenthetical "(applied to every rule alike)", the "128-d" and CVaR threshold-step details (A10 not applied).

## Not applied / open for Herlock
- A10 threshold step size (eta_t = 0.05 IMDb, 0.005 Adult) is not stated; no room. Only matters if E5 stays.
- t statistics kept at his population-std values (40/19/11 with sample std would be the alternative).
- Fig. 2 is now small (about 1.3 in tall); legible at print size but he may prefer to drop a table row instead.
- Remaining FILLIN: his exact-penalty arXiv number (line ~723).

## Appendix (Step 6, separate file, not referenced by main.tex)
- appendix.tex: (A) full proof of the rate theorem in his notation; (B) the closed-form
  infeasible-regime numbers for IMDb beta=3 (p-hat ~ min(p, r), l1 gap 1.58, floors 82.9 / 105.9,
  exact bias 30.7, M >= 454, uniform floor also 105.9); (C) the five Adult severity rows
  (population-std t: 44.7 / 69.4 / 35.2 / 35.8 / 7.1); (D) Adult per-race table.
- Compiles to one page with his preamble (review/appendix_preview.pdf; page 1 there is stub
  labels only). Two display equations slightly exceed the column width; harmless in a draft.
- Cross-references (thm:rate, lem:unbiased, lem:variance, thm:infeasible, cor:batchsize,
  tab:severity) resolve against his labels when pasted into main.tex after the bibliography.
