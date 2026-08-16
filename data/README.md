# Data

Two kinds of files: **committed datasets** (inputs) and **saved loss curves**
(`*_curves.npz` / `*.npz`, written by the scripts so figures can be replotted without
retraining — always prefer replotting from these).

## Datasets

| File | What it is |
|---|---|
| `imdb_wiki.csv` | Age + image-path metadata for the IMDb-Wiki face dataset |
| `imdb_embeddings.npy` | 128-d ResNet face embeddings keyed by image path — committed so **no 7 GB image download or PyTorch is needed** |
| `adult.csv` | Adult (Census Income) cache for the fairness experiments |
| `ICASP_2026.zip` | Original notebook-era bundle |
| `mnist_cache.npz` | *(git-ignored)* MNIST cache; regenerate with `scripts/ram_study/prep_mnist_cache.py` |

## Saved curves (file → producing script)

| File | Producing script |
|---|---|
| `imdbwiki_infeasible_K3_4000rounds_curves.npz` | `imdbwiki_infeasible_4k.py` |
| `imdbwiki_feasible_K3_5000rounds_curves.npz` | `imdbwiki_feasible_5k.py` |
| `adult_race_K3_2000rounds_curves.npz` | `adult_fairness.py` |
| `imdbwiki_cvar_K3_4000rounds_curves.npz` | `imdbwiki_cvar_fedavot.py` |
| `imdbwiki_cvar_feasible_K3_4000rounds_curves.npz` | `imdbwiki_cvar_feasible.py` |
| `imdbwiki_cvar_a09_K3_4000rounds_curves.npz` | `imdbwiki_cvar_a09_infeasible.py` |
| `imdbwiki_cvar_feasible_a09_K3_4000rounds_curves.npz` | `imdbwiki_cvar_a09_feasible.py` |
| `imdbwiki_cvar_grid_K3_4000rounds.npz` | `imdbwiki_cvar_grid.py` |
| `imdbwiki_regularized_K3_4000rounds_curves.npz` | `regularized_transport_sweep.py` |
| `imdbwiki_infeasible_bias_check.npz` | `infeasible_bias_check.py` |
| `ram_feasibility.npz` | `ram_feasibility_diagnostic.py` |
| `ram_cvar_vs_fedavot_1500rounds.npz` | `ram_cvar_vs_fedavot.py` |

The big per-round sweep CSVs are **not** here — they live in `results/` (see its README).
