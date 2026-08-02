"""
Sanity check: compare our from-scratch PCA against scikit-learn's
battle-tested implementation on the same dataset.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA

from pca_from_scratch import pca_from_scratch, explained_variance_ratio

digits = load_digits()
X, y = digits.data, digits.target

# --- Our implementation ---
X_2d_scratch, eigvals, _, _ = pca_from_scratch(X, n_components=2)
explained_scratch = explained_variance_ratio(eigvals, 2)

# --- scikit-learn implementation ---
pca = PCA(n_components=2)
X_2d_sklearn = pca.fit_transform(X)
explained_sklearn = pca.explained_variance_ratio_

print("Explained variance ratio:")
print(f"  from scratch : PC1={explained_scratch[0]:.4f}  PC2={explained_scratch[1]:.4f}")
print(f"  scikit-learn : PC1={explained_sklearn[0]:.4f}  PC2={explained_sklearn[1]:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
axes[0].scatter(X_2d_scratch[:, 0], X_2d_scratch[:, 1], c=y, cmap="tab10", s=15)
axes[0].set_title("From Scratch (NumPy + eigendecomposition)")

axes[1].scatter(X_2d_sklearn[:, 0], X_2d_sklearn[:, 1], c=y, cmap="tab10", s=15)
axes[1].set_title("scikit-learn PCA()")

plt.tight_layout()
plt.show()
