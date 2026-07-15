# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A research code repository for an ICASSP 2026 paper on **FedAVOT** — a federated-learning
aggregation scheme that uses **Optimal Transport (via masked IPFP)** to correct for the
mismatch between how often clients are *available/selected* and how much they *should*
count toward the objective. The paper is **arXiv:2509.14444** ("FedAVOT: Exact Distribution
Alignment in Federated Learning via Masked Optimal Transport", Rahimi & Kalogerias), already
accepted to ICASSP 2026; this repo produces its experiments section. Every experiment
compares aggregation rules against two anchors:

- **FedAVOT** — reweights the K selected clients each round using a transport plan.
- **FedAvg(K)** — partial-participation baseline: `sum_{i in S} (N/K)*p_i*theta_i`.
- **FedAvg(full)** — full-participation reference: `sum_i p_i*theta_i` over all clients.

There is no build system, package, or test suite. The deliverables are the figures
(`figures/*.png` / `.pdf`) and the paper text fragments (`paper/*.tex`).

## NOTATION WARNING (code vs paper)

The paper and the code name the two transport matrices **in reverse**:

| Concept | Paper (arXiv:2509.14444) | This repo's code |
|---|---|---|
| Transport coupling (marginals p and q) | `T` | `Y` |
| Normalized aggregation weights | `Y[i,j] = T[i,j]/q_j` | `T` |

Also: the paper's `q` is the availability distribution **over subsets** `A_j`; the code's
per-user `r` merely induces it, and the code's `q` (subset marginal) equals the paper's `q`.
Paper symbols: model `theta`, LR `eta_theta`, local epochs `H`, objective
`F(theta) = sum_i p_i f_i(theta)`, "users" not "clients". `paper/*.tex` follows the PAPER
convention. When writing paper text from code, translate.

## Repo layout

- `icasp_paper.ipynb` (root) — notebook artifact (linear-regression + MNIST cells, phase
  boundary). Historically the main artifact; the newer experiments live in `scripts/`.
- `data/` — committed datasets (`imdb_wiki.csv`, `imdb_embeddings.npy` = 128-d ResNet face
  embeddings keyed by image path, `ICASP_2026.zip`) **and saved loss curves** (`*_curves.npz`,
  written by the newer scripts so figures can be replotted without retraining).
- `scripts/` — standalone experiment scripts (see below).
- `figures/` — generated `.png`/`.pdf` outputs (committed; the `.pdf`s go to the Overleaf).
- `paper/` — LaTeX fragments for the paper + local preview (see "Paper text" below).

All paths inside the notebook and scripts are **repo-root-relative**, so always run from
the repo root.

## Running

Use the checked-in virtualenv (`.venv/`, git-ignored but on disk: Python 3.13, numpy 2.5,
matplotlib 3.11, scikit-learn 1.9, pandas 3.0, pypdf):

```powershell
.venv/Scripts/python.exe scripts/<name>.py
```

IMDb-Wiki scripts run in ~2–5 minutes (vectorized batched training, 128-d embeddings);
the synthetic scripts are similar. Only the notebook's MNIST cell and `icasp2025.py`
are heavy. To iterate, lower `ROUNDS`/`SEEDS` in the ALL-CAPS config block at the top
(no CLI). Newer scripts save raw curves to `data/*_curves.npz`; prefer replotting from
those over retraining (see `scripts/cvar_alpha_trend.py` for the pattern).

### Scripts

Earlier standalone snapshots: `icasp2025.py` (MNIST), `lin_reg_last_one.py` (synthetic).
Diagnosis + paper experiments (2026-07):

- `feasibility_diagnostic.py` → `figures/fedavot_mechanism.*` — the mechanism figure
  (achieved weight vs target with the `pi_i` ceiling; IPFP row-error trajectories).
- `phase_boundary_experiment.py` → `figures/fedavot_phase_boundary.*` — synthetic alpha
  sweep; feasible/infeasible loss panels + phase-boundary panel.
- `feasible_5k_rounds.py` — the phase-boundary feasible panel (alpha=0.5) at 5000 rounds.
- `imdbwiki_infeasible_4k.py` — script reproduction of the notebook's main IMDb-Wiki cell
  (mirrored cubic p/r, INFEASIBLE). Quotable: FedAVOT 116.40 ± 0.53, FedAvg(K)
  129.33 ± 0.04, FedAvg(full) 83.07 (tail-500, 5 seeds).
- `imdbwiki_feasible_5k.py` — FEASIBLE real-data variant: same clients/embeddings/p, but
  availability ALIGNED with importance (linear skew) → 0/100 infeasible, IPFP row_err 5e-9.
  Quotable: FedAVOT 88.82 ± 0.19 vs full 83.07. **FedAvg(K) diverges here** (its fixed N/K
  scaling assumes uniform participation; script freezes it at a 1e12 cap).
- `infeasible_bias_check.py` — no training; p_hat from stalled IPFP + closed-form
  weighted-LS optima on IMDb-Wiki → validates Sec 3.3's bias bound (see finding 6).
- `regularized_transport_sweep.py` → `figures/imdbwiki_regularized_*` — lambda-penalized
  (unbalanced) masked Sinkhorn sweep on the mirrored regime, kappa = 0..1 trained in
  parallel per draw; endpoints = uniform averaging / plain IPFP (see finding 6).
- `imdbwiki_cvar_*.py` — the FED-CVaR-AVG study (arXiv:2309.14176, Theodoropoulos/
  Nikolakakis/Kalogerias; code: github.com/PeriklisTheodoropoulos/risk-aware-FL):
  `_fedavot` (infeasible, alpha=0.3), `_feasible` (aligned), `_grid` ((alpha,gamma) grid +
  hinge-tilted-aggregation variant), `_a09_*` (near-risk-neutral bookend),
  `cvar_alpha_trend.py` (summary figure from saved npz).
- `adult_fairness.py` → `figures/adult_race_K3_2000rounds.*` — Adult (Census Income)
  fairness experiment for the OT-SGD paper (fills the paper's promised-but-missing Adult
  results; data cached at `data/adult.csv`). Group-homogeneous clients by race (users per
  group ∝ prevalence: 85/10/3/1/1), group-uniform importance p (1/5 per race), binary
  logistic regression. Both regimes in one script/figure: PREVALENCE (uniform r → 5/100
  infeasible users, 60% p-mass, IPFP stalls 1.7e-1): FedAVOT 0.2278 ± 0.0018,
  FedAvg(K) 0.6720 ± 0.0886, full 0.2068; ALIGNED (r ∝ p, feasible, 2.9e-8): FedAVOT
  0.2076 ≈ full 0.2068, **FedAvg(K) diverges**. Design is new (Amtej's Oct-2025 Adult
  pipeline was never committed) — needs Herlock's sign-off before entering the paper.

## Paper text (`paper/`)

- `experimental_setup.tex`, `experimental_results.tex` — fragments in the PAPER notation,
  written as **subfiles** of `preview.tex`: each compiles standalone (borrows the preview
  preamble) or via the combined `preview.tex`. When pasting into the Overleaf (Herlock's),
  copy only what is BETWEEN `\begin{document}` and `\end{document}`.
- Local compilation: `tectonic paper/preview.tex` (tectonic 0.16.9 on PATH). The VS Code
  LiveLaTeX extension compiles whichever file is open and ignores `% !TEX root` magic
  comments; the subfiles structure exists precisely so that still works. `paper/*.pdf` is
  git-ignored.
- Both fragments were pasted into the Overleaf on 2026-07-11. Overleaf pending checks:
  (a) if the methods section already states the feasibility condition, replace the inline
  `p_i <= pi_i` reminder with a `\ref`; (b) the methods mention a lambda-regularized
  feasible/infeasible transition — our experiments run UNREGULARIZED masked IPFP, align
  the wording.

## Core algorithm (shared across files)

The transport machinery is duplicated near-verbatim in each file. The pipeline:

1. Distributions over `N` clients: importance `p` and per-user availability `r` (both
   ALL-CAPS-config-controlled skews; `idx**a` vs `idx[::-1]**a`).
2. **`all_K_subsets_1based(N, K)`** → every size-`K` subset (transport columns).
   NOTE: subsets are **1-based tuples**; `build_mask` converts to 0-based rows. This
   1-based/0-based split is a persistent footgun.
3. **`estimate_q`** (vectorized Gumbel top-K MC) → subset marginal `q`.
4. Masked IPFP (Sinkhorn-style alternating scaling) fits the coupling with row marginal
   `p` and column marginal `q`; columns normalized to convex FedAVOT weights. Validity via
   the printed row error — in the mirrored IMDb-Wiki regime it CANNOT converge (stalls at
   ~4e-2); that is the point, not a bug.
5. Training loop: sample subset `j ~ q`, update all global models in parallel from the
   same draw so loss curves are directly comparable.

## Conventions

- All knobs in an ALL-CAPS config block at the top of each script; no CLI.
- Plot colors: FedAVOT = blue, FedAvg(K) = orange, FedAvg(full) = red, CVaR-combination =
  green, CVaR-uniform = purple, tilt variant = olive.
- Figure filenames embed the regime and `K`/`ROUNDS`; save both `.png` (Discord) and
  `.pdf` (paper), plus curves to `data/*_curves.npz`.
- Windows/PowerShell encoding footgun: piping script text through `Get-Content`/
  `Set-Content` mangles UTF-8 (alpha/gamma/em-dash → mojibake) and adds BOMs. Use the
  Edit/Write tools or `[IO.File]::ReadAllText/WriteAllText` with UTF8, and check figure
  legends after regex-editing scripts.

## Research findings so far (for the paper narrative)

The original question "why does FedAVOT fail to converge?" is RESOLVED and now has a
full experimental story:

1. **Diagnosis**: not a bug — the mirrored cubic `p`/`r` makes the transport problem
   infeasible. Feasibility requires `p_i <= pi_i` (inclusion probability). In the notebook
   config (N=100, K=3): 41/100 users infeasible holding ~88% of importance mass → hard
   floor on the p-weighted loss. One-liner: *FedAVOT corrects participation bias but
   cannot fix support collapse.*
2. **Feasible regime works, on real data too**: aligned availability → FedAVOT ~5.7 MSE
   above full (vs ~33 mirrored), stable through 5000 rounds. Synthetic: tracks full at
   ratio 1.01 when feasible; degrades to 8.4x as infeasible mass → 87%.
3. **FedAvg(K) diverges under aligned availability** (fixed N/K scaling presumes uniform
   participation); FedAVOT is immune (convex weights). Strengthens the paper.
4. **CVaR study (Herlock's request, concluded 2026-07-11)**: combining FED-CVaR-AVG with
   FedAVOT HURTS at every (alpha,gamma); unstable at alpha=0.1 (hinge multiplier ×
   extreme transport weights). Risk-aversion helps in NO regime: as alpha→1 both schemes
   improve monotonically. The real finding: **plain uniform averaging over the drawn
   subset beats FedAVOT in the infeasible regime** (108.5 vs 116.4 overall; 112.3 vs
   123.3 on infeasible users) — the gains earlier attributed to CVaR were from uniform
   aggregation. In the feasible regime FedAVOT wins (89.1 vs 94+). The "why" is now
   RESOLVED quantitatively (see finding 6).
5. Residual ~7% FedAVOT-to-full gap in the feasible regime is consistent with K=3
   sampling variance at fixed LR (unverified: LR decay should shrink it).
6. **Theory-experiment bridge for the infeasible case (2026-07-15, Problem 2 of the
   complete.tex review)**: the stalled IPFP delivers exactly the surrogate marginal
   p_hat = Y·1 (columns match q, so expected per-round weight of user i is p_hat_i);
   in the mirrored IMDb-Wiki regime p_hat ≈ min(p, pi) renormalized, ||p - p_hat||_1 =
   1.58. Linear regression → closed-form optima: F_p optimum 82.9 (matches measured
   full 83.07), surrogate floor F_p(theta_phat*) = 105.9, so the marginal shift alone
   explains 22.9 of the 33.3 measured gap (`scripts/infeasible_bias_check.py`).
   Running Sec 3.3's lambda-penalized transport (unbalanced Sinkhorn; kappa =
   lambda/(lambda+1) row-power update; kappa=0 IS uniform averaging, kappa=1 IS plain
   IPFP) shows **lambda tunes variance, not bias, under severe infeasibility**: floors
   flat at 104-106 for all lambda, measured loss rises 108.3 → 116.5 with lambda
   (`scripts/regularized_transport_sweep.py`). This resolves finding 4's open question:
   uniform wins because same floor + minimal weight variance. Footguns: the damped form
   Y *= (p/rowsum)^kappa has a kappa-independent fixed point (wrong problem); the u-v
   scaling form overflows at kappa=1 (use dense bounded-Y IPFP there).

Known estimation artifact (pre-existing): 1M MC samples can't cover C(100,3)=161,700
subsets; a cleaner formulation would run IPFP on per-user participation marginals.
