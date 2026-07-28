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
- `ram_feasibility_diagnostic.py` → `figures/ram_feasibility_diagnostic.*` — transport
  geometry of the FED-CVaR-AVG paper's own setting (arXiv:2309.14176 = "Federated
  Learning Under Restricted User Availability"; their `script for Mnist.py`). N=30 users,
  3 rarest hold digits 8,9 exclusively, RAM seed 2517 chosen so the availability tail
  (0.0061/0.0077/0.0107) matches their Table 1. Sweeps `users_per_round` R. Headline:
  **their published R=1 makes FedAVOT vacuous** (singleton batch → normalized weight ≡ 1
  → FedAVOT *is* FedAvg-relay), 16/30 users infeasible against a uniform target holding
  53% of its mass; feasibility (`p_i <= pi_i`) first holds at **R=6**, where IPFP
  converges to 1e-10. Also introduces the **enumeration-free transport solver** (below).
- `ram_cvar_vs_fedavot.py` → `figures/ram_cvar_vs_fedavot_1500rounds.*` — the training
  experiment in that setting: MNIST (64 PCA dims + bias, multinomial logistic), 30 users,
  their data split, R in {1,3,6} × (alpha,gamma) in {(1,1),(0.3,0.3),(0.1,0.1)}, 1500
  rounds, 3 seeds, identical RAM draws. Five rules: FedAvg-relay (their baseline),
  FED-CVaR-AVG (their Alg 1), FedAVOT, FedAVOT+CVaR, and Horvitz--Thompson relay.
  Metrics: overall test accuracy, accuracy on the rare users' digits, p-weighted train
  loss. `--smoke` shrinks it to a 1-minute shape check.
- `prep_mnist_cache.py` — one-off, fetches MNIST to `data/mnist_cache.npz` (git-ignored).
- `replot_paper_figures.py` — regenerates the three curve-based paper figures (IMDb-Wiki
  infeasible/feasible, Adult) from the saved `data/*_curves.npz` with the **de-federated
  vocabulary** (2026-07-27, Herlock's request): users/clients → critical groups, round →
  iteration, FedAvg(K) → fixed multiplier `m/K`, FedAvg(full) → full coverage, FedAVOT
  unchanged. No retraining, so the numbers quoted in the tex stay exactly valid.
  `phase_boundary_experiment.py` and `feasibility_diagnostic.py` have no saved curves;
  their labels were edited in place and the scripts re-run (both reproduce their quoted
  numbers exactly). **If you touch a paper figure, check the rendered PDF text, not just
  the prose** — the FL vocabulary was baked into the images and survived a full prose
  reframe unnoticed.
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

7. **Why our CVaR results looked "odd" to Herlock — RESOLVED (2026-07-27)**. Herlock
   asked (7/27) to test CVaR vs FedAVOT in the setting of "Restricted user availability
   in Federated Learning" — which is the SAME paper as the CVaR one (arXiv:2309.14176,
   real title "Federated Learning Under Restricted User Availability"). Three results:
   (a) **Their published setting makes the comparison degenerate.** Their RAM relays
   `users_per_round = 1`: the server broadcasts the single selected user's (theta, t) as
   the new global model, so there is no aggregation step. A singleton batch has one
   transport weight and it is forced to 1, so **FedAVOT is identically FedAvg-relay**
   there (confirmed: identical to 4 decimals in every seed). Their setting is also
   severely infeasible for a uniform target — 16/30 users, 53% of the target mass;
   feasibility first holds at R=6 (`ram_feasibility_diagnostic.py`).
   (b) **The two schemes act on different axes**: CVaR reweights ACROSS rounds
   (step-size amplification), FedAVOT WITHIN a round (aggregation weights). Sweeping R
   swaps them. MNIST, their split, 1500 rounds, 3 seeds, rare-digit test accuracy:
   R=1 FedAvg 0.613 = FedAVOT 0.613, FED-CVaR-AVG 0.779 (**their result reproduces**);
   R=6 FedAVOT 0.788 > FED-CVaR-AVG 0.775, and FedAVOT+CVaR is best at 0.851 vs full
   participation 0.795.
   (c) **The apparent contradiction with finding 4 is a metric difference, not a
   disagreement.** On the p-weighted objective FedAVOT is built to minimise, adding CVaR
   always costs (R=6: FedAVOT 0.2670 vs +CVaR 0.2750/0.2789; full 0.2645); on the
   rare-group accuracy their paper reports, adding CVaR always helps. Both papers are
   right about different objectives (`figures/ram_metric_disagreement_1500rounds.*`).
   Caveat for the paper's HT paragraph: the Horvitz--Thompson relay did NOT diverge here
   and was the best method at R=1 (rare 0.800) — its weights only reach 5.5x. Note
   `p_i <= pi_i` is exactly the condition `p_i/pi_i <= 1`, i.e. **feasibility is the same
   condition as HT weights being bounded** (at R=1 the 16 users with weight > 1 are
   exactly the 16 infeasible ones; at R=6 all weights are <= 0.83). So "unbounded" should
   not be written as "diverges" — the severity depends on the ratio and on whether the
   loss is bounded (CE here vs unbounded MSE in the IMDb-Wiki runs).

Known estimation artifact (pre-existing, now FIXED in the RAM scripts): 1M MC samples
can't cover C(100,3)=161,700 subsets. `scripts/ram_feasibility_diagnostic.py` replaces
enumeration entirely: masked IPFP converges to a product form `Y[i,S] = u_i v_S 1{i in S}`,
so column-normalizing gives `w_i(S) = u_i / sum_{j in S} u_j` and the whole plan is fixed
by the N-vector `u` solving `E_S[w_i(S) 1{i in S}] = p_i`. Fit it by multiplicative
updates over Monte-Carlo RAM draws — no C(N,K) matrix, any K. Validated to 4e-10 against
the enumerated masked IPFP on a feasible instance (`--validate`). **Footgun:** run it in
LOG space (`log_u += log p - log p_hat`, recentred). Under infeasibility `log u` diverges
for the starved users — that divergence IS the stall — so any absolute floor on `u`
silently flattens the plan and wrecks the fit (an earlier `clip(u, 1e-30)` turned a
correct `||p-p_hat||_1 = 0.03` into 0.25). Compare on a FEASIBLE instance only: when
infeasible neither iteration has a fixed point and the two stalls need not coincide.
