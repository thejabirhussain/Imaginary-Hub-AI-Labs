# Lecture 1 Notes: Linear Algebra for Machine Learning
**Module 2: In-Depth Lectures (AI Research)**  
*Week 1: Vectors, Systems of Linear Equations, and Matrix Elimination*

---

## 1. The Core Goal of Linear Algebra

The fundamental goal of linear algebra is to find a solution for a given set (system) of linear equations. 

We represent a system of equations in matrix notation as:
$$Ax = b$$

Where:
* $A$ is the **coefficient matrix** (size $m \times n$) containing the weights/factors.
* $x$ is the **unknown vector** (size $n \times 1$) containing variables we want to solve for.
* $b$ is the **target vector** (size $m \times 1$) containing outputs/labels.

### Step-by-Step Example System (2D)
Let's consider the system:
1. $2x - y = 0$
2. $x - 4y = 3$

In matrix format $Ax = b$:
$$\begin{bmatrix} 2 & -1 \\ 1 & -4 \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} 0 \\ 3 \end{bmatrix}$$

---

## 2. Three Perspectives on a Linear System

We can visualize and compute solutions using three distinct viewpoints.

### A. The Row Picture (Geometric Intersection)
The Row Picture looks at each equation individually as a geometric shape:
* In 2D: Intersecting lines in a plane.
* In 3D: Intersecting planes in space.

To solve the system, we find the common intersection point.
* For the system above, drawing the line $y = 2x$ and $x - 4y = 3$ on a coordinate grid shows they intersect at the unique point:
  $$x = -\frac{3}{7}, \quad y = -\frac{6}{7}$$

> [!WARNING]
> **Why the Row Picture Fails in Machine Learning**:
> Human visualization collapses beyond 3 dimensions. If you train a model with 100 features (dimensions) or fine-tune an LLM with billions of parameters, you cannot visualize the row picture of intersecting hyperplanes. Line intersection algorithms are also computationally expensive to scale.

### B. The Column Picture (Linear Combination)
Instead of lines intersecting, the Column Picture treats the system as a **linear combination of column vectors**. We seek scalars $x$ and $y$ that scale the column vectors of $A$ to sum exactly to vector $b$:
$$x \begin{bmatrix} 2 \\ 1 \end{bmatrix} + y \begin{bmatrix} -1 \\ -4 \end{bmatrix} = \begin{bmatrix} 0 \\ 3 \end{bmatrix}$$

* This shifts our view from geometry to arithmetic.
* Computers, GPUs, and vector engines are highly optimized for this "numbers game" because vector scaling and adding operations can be run in parallel.

### C. The Matrix View
Representing the system as a transformation of space: the matrix $A$ acts on the input vector $x$ to map it to the target vector $b$.

---

## 3. Systematic Row Elimination (Gaussian Elimination)

To solve systems of equations algebraically at scale, computers use **Gaussian Elimination** to simplify the coefficient matrix $A$ into an **Upper Triangular Matrix ($U$)**.

### Core Terms
* **Pivots**: The diagonal coefficients we divide by or eliminate rows with. 
  > [!IMPORTANT]
  > **Pivot Rule**: A pivot element can **never be zero**. If a pivot is zero, row operations must swap it with a non-zero row below.

### The Elimination Process (Step-by-Step 3x3)
Let's eliminate the values below the pivots to reach $U$:
$$\text{Augmented Matrix: } [A \mid b] = \begin{bmatrix} 1 & 2 & 1 & \mid & b_1 \\ 3 & 8 & 1 & \mid & b_2 \\ 0 & 4 & 1 & \mid & b_3 \end{bmatrix}$$

1. **Pivot 1** is $1$ (at index row 1, col 1).
2. Eliminate the $3$ below it in row 2: Subtract $3 \times (\text{Row 1})$ from $(\text{Row 2})$.
   $$\begin{bmatrix} 1 & 2 & 1 \\ 0 & 2 & -2 \\ 0 & 4 & 1 \end{bmatrix}$$
3. **Pivot 2** is $2$ (at index row 2, col 2).
4. Eliminate the $4$ below it in row 3: Subtract $2 \times (\text{Row 2})$ from $(\text{Row 3})$.
   $$\begin{bmatrix} 1 & 2 & 1 \\ 0 & 2 & -2 \\ 0 & 0 & 5 \end{bmatrix} = U \quad \text{(Upper Triangular Matrix)}$$

### Back Substitution
Once we have $U$, we solve bottom-up:
1. Find $z$ from the bottom row ($5z = \text{target}_3$).
2. Substitute $z$ into the second row to find $y$.
3. Substitute $y$ and $z$ into the first row to find $x$.

---

## 4. Singular Matrices & Elimination Failures

Elimination can fail when diagonal pivot elements become zero.

### A. Temporary Failure (Swappable Zero Pivot)
If we encounter a zero pivot in a row, but there is a non-zero element below it, we can swap rows using a **Permutation Matrix** ($P$). This fixes the pivot and allows elimination to continue.

### B. Permanent Failure (Singular Matrix)
If a pivot is zero and there are **no rows left below to swap**, the system has a permanent failure.
* The matrix $A$ is **singular** (non-invertible).
* The equations are dependent or parallel, meaning there is **no unique solution** (either infinite solutions or no solution).
* In Machine Learning, singular covariance matrices or weight gradients cause training pipelines to crash (vanishing/exploding gradients).

---

## 5. Elimination & Permutation Matrices

Computers perform row operations algebraically using matrix multiplication instead of loops.

### A. Elimination Matrices ($E_{21}$, $E_{32}$)
An elimination matrix $E_{ij}$ is formed by placing the multiplier (negative) in the identity matrix at coordinates $(i, j)$.
* To subtract $3 \times (\text{Row 1})$ from $(\text{Row 2})$ in a 3x3 matrix:
  $$E_{21} = \begin{bmatrix} 1 & 0 & 0 \\ -3 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
  Multiplying $E_{21} A$ performs the subtraction algebraically.

### B. Permutation Matrices ($P$)
A permutation matrix $P$ is formed by swapping rows on the Identity Matrix ($I$).
* To swap Row 1 and Row 2 in a 3x3 matrix:
  $$P_{12} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
  Multiplying $P_{12} A$ swaps Row 1 and Row 2 of $A$.

### Summary Algebraic Equation
The entire Gaussian elimination process is summarized in a single matrix equation:
$$(E_{32} E_{21}) A = U$$

---

## 6. Fundamental Laws of Matrix Algebra

When manipulating matrix operations, keep these core algebraic laws in mind:

1. **Matrix Multiplication is Non-Commutative**:
   $$AB \neq BA$$
   *Explanation*: The order of matrix operations matters. Applying row operation $A$ then $B$ is not the same as applying $B$ then $A$.
2. **Matrix Multiplication is Associative**:
   $$A(BC) = (AB)C$$
   *Explanation*: You can group matrix operations in any order without changing the final output matrix.
