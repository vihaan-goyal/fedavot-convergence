# Paper

LaTeX fragments for the ICASSP 2026 paper (**arXiv:2509.14444**, "FedAVOT: Exact
Distribution Alignment in Federated Learning via Masked Optimal Transport",
Rahimi & Kalogerias — accepted). These files use the **paper notation**, which names the
transport matrices in reverse from the code — see the NOTATION WARNING in `../CLAUDE.md`.

| File | What it is |
|---|---|
| `experimental_setup.tex` | Experiments-section setup fragment (subfile of `preview.tex`) |
| `experimental_results.tex` | Experiments-section results fragment (subfile of `preview.tex`) |
| `preview.tex` | Local preview wrapper: compiles both fragments with the shared preamble |
| `complete_tex_review.md` | 2026-07-15 review of the Overleaf `complete.tex` (clarity/narrative pass, Herlock's request) with the Problem-1/2 findings |

- Compile locally: `tectonic paper/preview.tex` (each fragment also compiles standalone —
  that's why the subfiles structure exists). `paper/*.pdf` is git-ignored.
- When pasting into the Overleaf, copy only what is **between** `\begin{document}` and
  `\end{document}`.
- Both fragments were pasted into the Overleaf on 2026-07-11; pending wording checks are
  listed in `../CLAUDE.md` ("Paper text").
- Figures referenced by bare filename resolve via `\graphicspath` →
  `../figures/2026-07-27_paper/`.
