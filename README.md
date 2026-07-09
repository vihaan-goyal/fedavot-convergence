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

## Contents

| File | What it is |
|------|------------|
| `icasp_paper.ipynb` | Main notebook. IMDb-Wiki age-regression experiments (real ResNet embeddings) + a self-contained **phase-boundary** section |
| `imdb_embeddings.npy` | Cached ResNet18 features (512-d → PCA 128, standardized) for the ~3,300 face crops the experiments use |
| `phase_boundary_experiment.py` | Standalone phase-boundary sweep (synthetic, controlled) → `fedavot_phase_boundary.png` |
| `icasp2025.py`, `lin_reg_last_one.py` | Earlier standalone MNIST / linear-regression experiments |
| `imdb_wiki.csv` | Age + image-path metadata for the IMDb-Wiki dataset |

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
