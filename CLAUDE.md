# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A research code repository for an ICASP 2026 paper on **FedAVOT** — a federated-learning
aggregation scheme that uses **Optimal Transport (via masked IPFP)** to correct for the
mismatch between how often clients are *available/selected* and how much they *should*
count toward the objective. Every experiment compares three aggregation rules:

- **FedAVOT** — reweights the K selected clients each round using a transport plan `T`.
- **FedAvg(K)** — exact partial-participation baseline: `sum_{i in S} (N/K)*p_i*theta_i`.
- **FedAvg(full)** — full-participation reference: `sum_i p_i*theta_i` over all clients.

There is no build system, package, or test suite. The deliverables are the figures
(`*.png` / `*.pdf`) produced by running the scripts/notebook.

## Repo layout

- `icasp_paper.ipynb` (root) — the main artifact.
- `data/` — committed datasets: `imdb_wiki.csv`, `imdb_embeddings.npy`, `ICASP_2026.zip`.
- `scripts/` — standalone experiment scripts (see below).
- `figures/` — generated `.png`/`.pdf` outputs (committed).

All paths inside the notebook and scripts are **repo-root-relative** (`data/...`,
`figures/...`), so always run from the repo root.

## Running

Use the checked-in virtualenv (`.venv/`, git-ignored but on disk: Python 3.13, numpy 2.5,
matplotlib 3.11, scikit-learn 1.9, pandas 3.0):

```powershell
.venv/Scripts/python.exe scripts/phase_boundary_experiment.py  # phase-boundary figure
.venv/Scripts/python.exe scripts/feasibility_diagnostic.py     # mechanism figure
.venv/Scripts/python.exe scripts/icasp2025.py                  # MNIST experiment
.venv/Scripts/python.exe scripts/lin_reg_last_one.py           # synthetic linear regression
```

Each script runs end-to-end (fetch/generate data → solve transport → train over `SEEDS`
→ save a `<domain>_K<K>_...png/.pdf` figure and `plt.show()`). Runs are heavy: `ROUNDS`
in the thousands × `SEEDS = [0,1,2,3,4]`, and FedAvg(full) retrains all `NUM_USERS`
clients every round. To iterate quickly, lower `ROUNDS`, `SEEDS`, or `NUM_USERS` in the
config block at the top of the file. `icasp2025.py` downloads MNIST via
`fetch_openml("mnist_784")` on first run.

`icasp_paper.ipynb` is the **current / most-developed artifact** (the file under active
git changes). It is a cleaned, refactored merge of the two scripts and diverges from
them: it runs at `K=3`, `ROUNDS=4000`, and partitions **real client data from
`imdb_wiki.csv`** (grouped by `client_id`) for the linear-regression cell, using an
exact `estimate_q` rather than the scripts' Monte-Carlo `estimate_q_by_mc`. When changing
the method, prefer editing the notebook; treat the `.py` files as earlier standalone
snapshots.

## Core algorithm (shared across all three files)

The transport machinery is duplicated near-verbatim in each file. The pipeline:

1. **`make_skew_distributions(N)`** → importance `p` and availability/selection `r`,
   two deliberately skewed distributions over `N` clients (this skew is the whole point —
   it's what FedAVOT corrects and FedAvg cannot).
2. **`all_K_subsets_1based(N, K)`** → every size-`K` client subset (the transport columns).
   NOTE: subsets are **1-based tuples**; `build_mask` converts to 0-based row indices.
   This 1-based/0-based split is a persistent footgun — respect it when touching indexing.
3. **`estimate_q`** (or `estimate_q_by_mc`) → target column marginal `q`: the probability
   each K-subset is drawn under `r`.
4. **`solve_T_with_given_subsets` / `solve_T`** → runs **masked IPFP** (`ipfp_masked`:
   Sinkhorn-style alternating row/col scaling, masked to allowed subset memberships) to
   fit joint `Y` with row-marginal `p` and col-marginal `q`, then `recover_T` normalizes
   each column to a convex weight vector. `T[:, j]` are the FedAVOT aggregation weights
   for subset `j`.
5. **Training loop**: each round samples a subset `j ~ q`, gets its members + `T`-weights
   via `column_users_and_weights`, and updates all three global models in parallel so the
   loss curves are directly comparable.

The learner is swappable and is the main axis of variation between files:
NumPy multinomial logistic regression (`icasp2025.py`) vs. plain linear-regression GD
(`lin_reg_last_one.py` / notebook). IPFP validity is checked via `T_col_err_inf` and
`p_match_err_inf` printed after solving — watch these when tuning `IPFP_TOL`/`IPFP_MAX_ITERS`.

## Conventions

- All experiment knobs live in an ALL-CAPS config block at the top of each script; there
  is no CLI. Figure filenames are f-strings embedding `K` (saved under `figures/`), so
  bumping `K` writes a new file.
- Plot color code is fixed: FedAVOT = blue, FedAvg(K) = orange, FedAvg(full) = red.
- `data/imdb_wiki.csv` (~13 MB) and `data/ICASP_2026.zip` are committed data assets; the
  generated figures in `figures/` are committed outputs. `.venv/` is git-ignored despite
  being on disk.

## Open research question: "Why does FedAVOT fail to converge?" (diagnosis)

This is the central question with the collaborator (Herlock). **Diagnosis: it is not a bug in
the FedOT update rule — the optimal-transport problem IPFP is asked to solve is infeasible by
construction, because of how `p` and `r` are defined.**

- The FedOT update is a convex combination, so it equals SGD with stochastic gradient
  `ĝ = Σ_{i∈S_j} T[i,j] g_i(w)`. Its expectation is `∇F(w)` (unbiased on the correct
  `p`-weighted objective) **only if** IPFP achieves the marginal `Σ_j q_j T[i,j] = p_i`.
- IPFP can only place weight on a client through subsets it appears in, so feasibility
  **requires `p_i ≤ π_i` for every client**, where `π_i = P(i ∈ sampled K-subset)` is its
  inclusion probability. This is a coverage / absolute-continuity condition — the same one
  importance sampling needs (proposal must cover the target support).
- `make_skew_distributions` sets `p = idx[::-1]**3` and `r = idx**3` — **exact cubic mirror
  images**, so the most important clients have ~zero availability. For the exact notebook
  config (N=100, K=3), **41 clients are infeasible (`p_i > π_i`) and they hold ~88% of the
  total importance mass**; the top users are infeasible by up to ~5 orders of magnitude.
- Runtime consequence: IPFP oscillates and hits `IPFP_MAX_ITERS` without matching the
  marginals (debiasing silently fails); the ~88% of `p`-mass on never-sampled clients is a
  hard floor on the `p`-weighted loss, so FedOT/FedAvg(K) plateau high while only
  FedAvg(full) — which trains everyone every round — descends. This is the "non-convergence."
- One-liner for the paper: **FedAVOT corrects participation bias but cannot fix support
  collapse.** Convergence needs `supp(p) ⊆ reachable set`, quantitatively `p ≼ π`.

Next steps:
1. **Make the failure visible** — ✅ DONE (`scripts/feasibility_diagnostic.py` → `figures/fedavot_mechanism.png`/`.pdf`).
   Two regimes side by side: scatter of achieved weight `mᵢ = Σⱼ qⱼ·T[i,j]` vs target `pᵢ` with the
   ceiling `πᵢ` overlaid, plus IPFP row-error-vs-iteration. Feasible (α=0.2): all clients on the
   diagonal, row_err→8e-11 in 56 iters, 0% `p`-mass undelivered. Infeasible (α=3.0): high-`p`
   clients pinned at `πᵢ` far below the diagonal, row_err stalls at 7.7e-2, **78% of `p`-mass
   undelivered = the loss floor**. This is the mechanism panel behind the phase boundary.
2. **Feasible-regime sweep** — ✅ DONE (`scripts/phase_boundary_experiment.py` → `figures/fedavot_phase_boundary.png`).
   Sweeps skew α; shows FedAVOT tracks FedAvg(full) when feasible and stalls when not, plus a
   phase-boundary panel (final loss vs % infeasible mass). NOTE: it labels α=0.5 the "feasible"
   regime, but α=0.5 is only ~14% infeasible and IPFP does *not* fully converge there — the
   mechanism figure uses α=0.2 (genuinely 0% infeasible) for the clean feasible baseline. Keep the
   two α labels straight if both figures go in the paper.
3. **Kill the estimation artifact**: 1M MC samples can't cover C(100,3)=161,700 subsets;
   reformulate IPFP on per-user participation marginals (100 numbers) instead of per-subset `q`.
4. **Confound to fix before final numbers**: `X_full = rng.randn(...)` uses random-noise
   features, not real IMDb-Wiki embeddings (only `age` is real). Shared across all methods so
   not the convergence cause, but swap in real embeddings before reporting.
