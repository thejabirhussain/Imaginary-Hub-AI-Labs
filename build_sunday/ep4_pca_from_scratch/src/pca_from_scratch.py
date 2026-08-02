"""
PCA From Scratch — no scikit-learn.

Implements Principal Component Analysis purely with NumPy, following the
eigendecomposition-of-the-covariance-matrix derivation covered in the
companion video and in in_depth_lectures_modules/foundations_of_ai/
pca_dimensionality_reduction_notes.md.

Steps:
  1. Center the data (subtract the mean of each feature/column).
  2. Compute the covariance matrix of the centered data.
  3. Compute eigenvalues & eigenvectors of the covariance matrix.
  4. Sort eigenpairs by eigenvalue, descending.
  5. Keep the top `n_components` eigenvectors -> principal components.
  6. Project the centered data onto those components.
"""

import numpy as np


def pca_from_scratch(X: np.ndarray, n_components: int = 2):
    """Run PCA on X using eigendecomposition of the covariance matrix.

    Parameters
    ----------
    X : np.ndarray, shape (n_samples, n_features)
        Raw input data.
    n_components : int
        Number of principal components to keep.

    Returns
    -------
    X_projected : np.ndarray, shape (n_samples, n_components)
        Data projected onto the top principal components.
    eigvals_sorted : np.ndarray, shape (n_features,)
        All eigenvalues of the covariance matrix, sorted descending.
    components : np.ndarray, shape (n_features, n_components)
        The top `n_components` eigenvectors (the principal component axes).
    mean : np.ndarray, shape (n_features,)
        The per-feature mean used to center the data (needed to project
        new/unseen points with the same transform later).
    """
    # Step 1: Center the data
    mean = X.mean(axis=0)
    X_centered = X - mean

    # Step 2: Compute the covariance matrix
    cov_matrix = np.cov(X_centered, rowvar=False)

    # Step 3: Compute eigenvalues & eigenvectors (covariance matrix is
    # always symmetric, so `eigh` is faster & numerically safer than `eig`)
    eigvals, eigvecs = np.linalg.eigh(cov_matrix)

    # Step 4: Sort in descending order
    order = np.argsort(eigvals)[::-1]
    eigvals_sorted = eigvals[order]
    eigvecs_sorted = eigvecs[:, order]

    # Step 5: Select top principal components
    components = eigvecs_sorted[:, :n_components]

    # Step 6: Project data onto the principal components
    X_projected = X_centered @ components

    return X_projected, eigvals_sorted, components, mean


def explained_variance_ratio(eigvals: np.ndarray, n_components: int) -> np.ndarray:
    """Fraction of total variance captured by each of the top components."""
    return eigvals[:n_components] / eigvals.sum()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from sklearn.datasets import load_digits

    # Load dataset: 1797 images of handwritten digits, 8x8 pixels -> 64 features
    digits = load_digits()
    X, y = digits.data, digits.target

    # Apply our from-scratch PCA
    X_2d, eigvals, components, mean = pca_from_scratch(X, n_components=2)
    print(f"{X.shape} -> {X_2d.shape}")

    explained = explained_variance_ratio(eigvals, 2)
    print(f"PC1: {explained[0]*100:.1f}% variance explained")
    print(f"PC2: {explained[1]*100:.1f}% variance explained")

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap="tab10", s=15)
    plt.xlabel(f"PC1 ({explained[0]*100:.1f}% variance)")
    plt.ylabel(f"PC2 ({explained[1]*100:.1f}% variance)")
    plt.title("64-D Digits Compressed to 2-D via PCA (from scratch)")
    plt.colorbar(label="Digit")
    plt.show()
