# fedavot-convergence

**When does optimal-transport-weighted federated averaging (FedAVOT) converge — and why does it fail?**

FedAVOT reweights the clients sampled each round with an optimal-transport plan `T` so that,
in expectation, each client's influence matches an **importance distribution `p`**, despite
clients being sampled from an **availability distribution `r`**. This repo studies when that
correction works and when it breaks.

## The finding

FedAVOT is unbiased SGD on the correct `p`-weighted objective **only if the transport is
feasible** — i.e. every important client actually shows up sometimes:

```
p_i ≤ π_i     where π_i = P(client i is in the sampled K-subset)
```

You can only reweight clients who participate; you cannot manufacture participation for clients
that are never available. When `p` and `r` are mismatched (here they are cubic mirror images),
the most important clients have ~zero availability, ~88% of the importance mass becomes
infeasible to route, IPFP can't match the marginals, and the loss stalls.

Crucially, infeasibility only **hurts** when the unreachable clients are *systematically
different* (distribution shift correlated with availability — the realistic non-IID setting).
Sweeping the skew gives a clean phase boundary: FedAVOT tracks the full-participation optimum
when feasible, and degrades **up to 8.4× worse** as infeasibility grows.

**One line:** *FedAVOT corrects participation bias, but it cannot fix clients that are never available.*

## Repo map

Every folder has its own `README.md` index — start there.

| Path | What it is |
|------|------------|
| [`figures/`](figures/README.md) | **All generated figures**, in dated per-experiment subfolders. The paper figures are `figures/2026-07-27_paper/`; the sweep-pipeline figures are `figures/2026-08-10_sweep_pipeline/` |
| [`scripts/`](scripts/README.md) | All experiment scripts, grouped by study (paper experiments, CVaR study, RAM study, the unified sweep pipeline) |
| [`results/`](results/README.md) | Dated run/analysis folders. The raw ~15 GB sweep is git-ignored; the committed folders are the derived deliverables (beats-baseline table, core-metrics figures + `core_metrics_report.html`) |
| [`sheets_export/`](sheets_export/README.md) | Curated CSVs behind the Google Sheets deliverable |
| [`data/`](data/README.md) | Committed datasets (IMDb-Wiki embeddings, Adult) + saved loss curves (`*_curves.npz`) for replotting without retraining |
| [`paper/`](paper/README.md) | LaTeX fragments for the ICASSP 2026 paper (arXiv:2509.14444, accepted) + the `complete.tex` review |
| `icasp_paper.ipynb` | The original notebook (IMDb-Wiki age regression + phase boundary); newer work lives in `scripts/` |
| `CLAUDE.md` | The full working log: notation warning (code vs paper), conventions, and the numbered research findings |

**Guided tour:** the mechanism and phase-boundary story is in `figures/2026-07-27_paper/`;
the 10×10 (α, γ) sweep outputs are in `figures/2026-08-10_sweep_pipeline/` (best-config
curves, pinned (0.3, 0.3) curves, heatmaps); the per-algorithm comparison deliverable —
point-ranges, per-client curves, per-group regret heatmaps — is
`results/2026-08-15_herlock_core_metrics/` (open `core_metrics_report.html` for everything
on one page).

Scripts are run from the repo root (paths inside them are root-relative), e.g.
`python scripts/phase_boundary_experiment.py`.

## Setup & run

```bash
git clone https://github.com/vihaan-goyal/fedavot-convergence.git
cd fedavot-convergence
pip install numpy pandas matplotlib scikit-learn jupyter
jupyter notebook icasp_paper.ipynb   # then Run All
```

The embeddings are committed, so **you do not need the 7 GB image dataset or PyTorch to run the
notebook** — those were only used to *build* `imdb_embeddings.npy`. Full run is a few minutes.

## Results at a glance (real IMDb-Wiki embeddings)

| Method | final MSE | RMSE | outcome |
|--------|-----------|------|---------|
| FedAvg (full) | 83 | **9.1 yr** | reaches the centralized least-squares optimum |
| FedAVOT | 120 | 10.9 yr | stalls above optimum under the skew |
| FedAvg (K) | 129 | 11.4 yr | no meaningful learning |

## Notes

- The **phase-boundary** figure uses synthetic data with availability-correlated drift (the
  controlled experiment that isolates the feasibility mechanism); the **IMDb-Wiki** cells use
  real embeddings.
- The real-embedding runs center the target ages and use `LR=1e-2`; without this the bias-free
  linear model underfits (it can't represent mean age from zero-mean features).
- ResNet18 is ImageNet-pretrained (not face/age-specialized), so RMSE ~9 yr is decent but not
  state-of-the-art — a face-specialized embedding would sharpen the signal.
