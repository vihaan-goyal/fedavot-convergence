# One-off: fetch MNIST from OpenML and cache a compact copy to data/mnist_cache.npz
# (uint8 pixels + labels, train/test split as in torchvision: first 60k / last 10k).
# The RAM/CVaR scripts load this instead of hitting the network. Cache is git-ignored.
import numpy as np
from sklearn.datasets import fetch_openml
import os

OUT = "data/mnist_cache.npz"
if os.path.exists(OUT):
    print(f"{OUT} already exists; nothing to do")
    raise SystemExit

print("fetching mnist_784 from OpenML (~55 MB, takes a minute)...")
mnist = fetch_openml("mnist_784", version=1, as_frame=False)
X = mnist.data.astype(np.uint8)          # (70000, 784), 0..255
y = mnist.target.astype(np.int64)        # (70000,)

np.savez_compressed(OUT,
                    X_train=X[:60000], y_train=y[:60000],
                    X_test=X[60000:], y_test=y[60000:])
print(f"saved {OUT}: train {X[:60000].shape}, test {X[60000:].shape}")
print("class counts (train):", np.bincount(y[:60000]))
