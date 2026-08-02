# Linear Algebra 03 / Week 4: Principal Component Analysis (PCA) & Dimensionality Reduction

## 1. The Curse of Dimensionality
Real datasets rarely live in 1 or 2 dimensions. A student's academic record alone (Math, Physics, Chemistry, ... across 8 semesters) can easily have **64 features**, meaning each student is a single point floating in **64-dimensional space**.
- Humans cannot visualize a 64-dimensional cloud of points directly.
- We still need to see the *shape* of that cloud — which students cluster together, which are outliers — to draw useful conclusions.
- **Principal Component Analysis (PCA)** solves this: it takes n-dimensional data and compresses it down to 2 or 3 dimensions **while preserving the same overall pattern** the full-dimensional cloud would have shown.

PCA does not invent new information. It re-expresses the existing data along the directions that matter most, and discards the directions that don't.

## 2. Step 1 — Calculate the Center (Mean)
For any set of points, the center (centroid) is the average position across every dimension:

$$ C(x, y) = \left( \frac{x_1 + x_2 + \dots + x_n}{n},\ \frac{y_1 + y_2 + \dots + y_n}{n} \right) $$

This generalizes directly to any number of dimensions — for 64-D data you just extend the same formula across all 64 coordinates: $C = (\bar{x_1}, \bar{x_2}, \dots, \bar{x_{64}})$. You never need to *visualize* 64 dimensions to compute this; it's pure arithmetic per column.

## 3. Step 2 — Re-center the Data to the Origin
Once we know the center, we subtract it from every point:

$$ x_i' = x_i - \bar{x} $$

- This does **not** change the shape or spread of the point cloud — only its coordinates relative to origin.
- Why bother? Working with numbers centered at zero drastically simplifies the variance/covariance math that follows (smaller, more numerically stable computations).
- PCA is not about *where* a point is located absolutely — it's about the **structure of the cloud**. Re-centering preserves that structure perfectly.

## 4. Step 3 — Variance: How Spread Out Is the Data?
**Variance** tells us how much a single feature is spread out (how "distinct" or "informative" it is).

$$ \text{Var}(x) = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n} $$

**Why variance matters:** if every data point has nearly the same value for a feature, that feature carries almost no distinguishing information — you cannot separate or rank points using it. The **more spread out** (higher variance) a feature is, the more useful it is for telling data points apart. PCA specifically hunts for the directions of *maximum variance* in the data.

## 5. Step 4 — Covariance: How Two Features Move Together
While variance describes a single feature, **covariance** describes the relationship between two features:

$$ \text{Cov}(x, y) = \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}{n} $$

- **Positive covariance**: as $x$ increases, $y$ tends to increase too (e.g. Math marks vs. Physics marks).
- **Negative covariance**: as $x$ increases, $y$ tends to decrease (e.g. hours spent gaming vs. CGPA).
- **Zero covariance**: the two features have no linear relationship.

## 6. Step 5 — The Covariance Matrix
For a dataset with multiple features, we assemble all pairwise variances and covariances into a single symmetric matrix. For a 2-feature example (Math, Physics):

$$ A = \text{Cov}(X) = \begin{bmatrix} \text{Var}(\text{Math}) & \text{Cov}(\text{Math}, \text{Physics}) \\ \text{Cov}(\text{Math}, \text{Physics}) & \text{Var}(\text{Physics}) \end{bmatrix} $$

This matrix `A` is the bridge between raw statistics and linear algebra — it becomes the input to eigendecomposition in the next step. For $n$ features, this generalizes to an $n \times n$ matrix.

## 7. Step 6 — Eigenvalues & Eigenvectors of the Covariance Matrix
Recall from eigendecomposition: for a matrix $A$, we solve for the vector $v$ and scalar $\lambda$ satisfying

$$ A v = \lambda v \quad\Longrightarrow\quad (A - \lambda I) v = 0 \quad\Longrightarrow\quad \det(A - \lambda I) = 0 $$

Applied to the **covariance matrix**, this eigendecomposition has a beautiful geometric meaning:
- Each **eigenvector** points in a direction along which the data is stretched.
- Each **eigenvalue** tells you *how much* variance exists along that eigenvector's direction.

## 8. Step 7 — Ranking Principal Components
Once you have all eigenvalue/eigenvector pairs of the covariance matrix:
- Sort the eigenvalues in **descending order**.
- The eigenvector with the **highest eigenvalue** becomes **PC1 (Principal Component 1)** — it captures the most information/variance in the dataset.
- The eigenvector with the **second-highest eigenvalue** becomes **PC2**, capturing the next-most variance, and so on.
- Since PC1 and PC2 come from a symmetric covariance matrix, they are automatically **orthogonal (perpendicular) to each other**.

## 9. Step 8 — Project the Data onto the Principal Components
Finally, project the (re-centered) data points onto the top-$k$ eigenvectors you selected:

$$ X_{\text{projected}} = X_{\text{centered}} \cdot [\,v_1 \ v_2 \ \dots\ v_k\,] $$

Plotting $X_{\text{projected}}$ gives you a 2D (or 3D) scatter plot that preserves the same clustering/pattern information the original n-dimensional cloud contained — just in a space humans can actually see.

## 10. Full Algorithm Summary
1. **Calculate the center** (mean) of every feature/column.
2. **Re-center** all points to the origin by subtracting the center.
3. **Calculate variance** for each feature.
4. **Calculate covariance** between every pair of features → build the **covariance matrix**.
5. **Compute eigenvalues & eigenvectors** of the covariance matrix (`numpy.linalg.eigh`, since the covariance matrix is always symmetric).
6. **Sort** eigenvalue/eigenvector pairs in descending order of eigenvalue.
7. **Select the top-$k$ eigenvectors** → these are PC1, PC2, ..., PCk.
8. **Project** the centered data onto the selected eigenvectors to get the final low-dimensional representation.

## 🎯 Why This Matters for Machine Learning
- **Dimensionality reduction**: compress high-dimensional features (images, embeddings, sensor data) into a manageable number of dimensions before feeding them into downstream models.
- **Visualization**: the only practical way to "see" a 64-D (or higher) dataset is to project it down to 2D/3D via PCA.
- **Noise reduction**: dropping low-eigenvalue components often removes noise rather than signal, since noise tends to contribute little variance.
- **Explained variance**: the ratio $\frac{\lambda_i}{\sum \lambda_j}$ tells you exactly what percentage of the dataset's total information each principal component retains — a direct, quantitative measure of how much you're allowed to compress before losing meaningful structure.

---
📺 Companion video: *I Built a PCA System From Scratch Using Eigendecomposition — No Scikit-Learn*
💻 Companion code: [`build_sunday/ep4_pca_from_scratch`](../../build_sunday/ep4_pca_from_scratch)
