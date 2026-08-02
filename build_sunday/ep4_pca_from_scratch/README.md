# Build Sunday EP 4: PCA From Scratch Using Eigendecomposition (No Scikit-Learn)

A from-scratch implementation of **Principal Component Analysis** built purely with **NumPy** — no `sklearn.decomposition.PCA` shortcuts. This project walks through the full mathematical pipeline (mean centering → covariance matrix → eigendecomposition → projection) and then validates the result against scikit-learn's implementation on a real 64-dimensional dataset.

---

## 🌟 Algorithm Flow

```
                ┌────────────────────────────────────────┐
                │      Raw Data (n_samples, n_features)   │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (subtract per-feature mean)
                ┌────────────────────────────────────────┐
                │            Center the Data              │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (np.cov)
                ┌────────────────────────────────────────┐
                │         Covariance Matrix (A)           │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (np.linalg.eigh)
                ┌────────────────────────────────────────┐
                │     Eigenvalues (λ) & Eigenvectors (v)  │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (sort descending by λ)
                ┌────────────────────────────────────────┐
                │   Rank Principal Components: PC1, PC2…  │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (X_centered @ components)
                ┌────────────────────────────────────────┐
                │     Projected Data (n_samples, k)       │
                └────────────────────────────────────────┘
```

---

## 🚀 Setup Instructions

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run the from-scratch PCA on the digits dataset (64-D → 2-D)
```bash
python src/pca_from_scratch.py
```
This loads `sklearn.datasets.load_digits` (used only as a ready-made 64-feature dataset, not for the PCA math itself), compresses it from 64 dimensions down to 2, prints the explained variance for PC1/PC2, and plots the result colored by digit label.

### 3. Compare against scikit-learn's PCA
```bash
python src/pca_sklearn_comparison.py
```
Runs both implementations side by side and prints their explained-variance ratios so you can confirm the from-scratch math matches the industry-standard implementation.

---

## 🛠️ How It Works

`pca_from_scratch(X, n_components)` in [`src/pca_from_scratch.py`](src/pca_from_scratch.py) does exactly six things:
1. **Center** — subtract the mean of each column so the dataset's centroid sits at the origin.
2. **Covariance matrix** — `np.cov(X_centered, rowvar=False)` captures how every pair of features varies together.
3. **Eigendecomposition** — `np.linalg.eigh(cov_matrix)` (covariance matrices are always symmetric, so `eigh` is faster & more numerically stable than the general-purpose `eig`).
4. **Sort** — eigenvalues/eigenvectors are returned in arbitrary order; sort descending by eigenvalue.
5. **Select** — keep the top `n_components` eigenvectors. The eigenvector with the largest eigenvalue is **PC1** (captures the most variance/information), the next is **PC2**, etc.
6. **Project** — `X_centered @ components` maps every point onto the new, lower-dimensional axes.

---

## 🎓 Learning Objectives

This codebase is specifically constructed to teach:
* **Why PCA exists**: the curse of dimensionality, and why "informative" data means "high variance" data.
* **The variance → covariance → covariance matrix chain**, and how it connects statistics to linear algebra.
* **Eigendecomposition as the engine of PCA**: eigenvectors are the new axes, eigenvalues rank how much information each axis holds.
* **Explained variance**: how to quantify exactly how much signal you keep (or lose) when compressing dimensions.
* **Validating a from-scratch implementation** against a trusted library (scikit-learn) — a habit worth building whenever you re-derive a well-known algorithm.

---

## 🔮 Future Improvements
1. **Whitening**: scale projected components by $1/\sqrt{\lambda_i}$ so every principal component has unit variance.
2. **Scree plot**: visualize eigenvalues in descending order to help pick `n_components` objectively (the "elbow" method).
3. **Standardization option**: add a `standardize=True` flag (z-score each feature before centering) for datasets where features live on very different scales.
4. **SVD-based implementation**: add an alternate solver using Singular Value Decomposition (`np.linalg.svd`) directly on the centered data, which avoids explicitly forming the covariance matrix and scales better to very high-dimensional data — the natural bridge to **Episode 5 (SVD + Recommendation Systems)**.

---
📺 Companion video: *I Built a PCA System From Scratch Using Eigendecomposition — No Scikit-Learn*
📚 Companion theory notes: [`in_depth_lectures_modules/foundations_of_ai/pca_dimensionality_reduction_notes.md`](../../in_depth_lectures_modules/foundations_of_ai/pca_dimensionality_reduction_notes.md)
