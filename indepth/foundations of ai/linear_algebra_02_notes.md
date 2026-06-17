# Linear Algebra 02: The Matrix Picture & Inverses

## 1. The Matrix Picture (Ax = b)
While the **Row Picture** visualizes equations as intersecting planes and the **Column Picture** visualizes them as linear combinations of vectors, the **Matrix Picture** is the most powerful computational view. 
By pulling out the coefficients into a matrix `A`, placing the unknowns in a vector `x`, and targeting the outputs in a vector `b`, we formulate the system as:
$$ Ax = b $$
This allows us to process systems at massive scale, which is the foundational engine of modern Machine Learning architectures.

## 2. Gaussian Elimination & The Upper Triangular Matrix (U)
To solve $Ax = b$ algorithmically, we use Gaussian Elimination. 
- The goal is to eliminate variables below the main diagonal by subtracting multiples of one row from another.
- This transforms the original matrix `A` into an **Upper Triangular Matrix (U)**, where all elements below the diagonal are zero.
- Once we have `U`, we solve for the variables from bottom to top using **Back Substitution**.

## 3. Recognizing "Bad Equations"
Not all systems have a unique solution. A system breaks if it contains "bad equations."
- **In the Row Picture:** This represents two planes that are perfectly parallel. They will never intersect.
- **In the Column Picture:** This represents vectors that lie on the same line (are parallel) and cannot span out to create the target vector `b`.
When training neural networks, encountering systems like this prevents the model from converging.

## 4. Zero Pivots: Temporary vs. Permanent Failure
The numbers on the main diagonal during elimination are called **Pivots**. A pivot can never be zero.
- **Temporary Failure:** If a pivot becomes zero, but there is a non-zero number in the rows below it, we simply swap the rows and continue elimination.
- **Permanent Failure (Singular Matrix):** If a zero pivot is pushed to the very bottom row and there is nothing left to swap, the elimination process fails permanently. The matrix is **Singular** (non-invertible) and the system has no unique solution. This scenario will crash a neural network training loop.

## 5. The Augmented Matrix: [ A | b ]
To keep the system balanced, whatever operations we perform on the left side of the equation (matrix `A`) must also be performed on the right side (vector `b`). 
We attach `b` as an extra column to `A` to form an **Augmented Matrix**. This ensures parity throughout the entire Gaussian Elimination process.

## 6. Elimination & Permutation Matrices
We do not subtract rows manually in code; we use Matrix Multiplication!
- **Elimination Matrices (E):** An operation like "subtract 3 times row 1 from row 2" is represented algebraically as an Elimination Matrix (e.g., $E_{21}$). Multiplying $E_{21} \cdot A$ executes the elimination step. This unified structure is exactly why GPUs can execute row operations in parallel incredibly fast.
- **Permutation Matrices (P):** To fix a temporary zero pivot failure, we swap rows using a Permutation Matrix. A permutation matrix is just the Identity Matrix `I` with its rows swapped. Multiplying $P \cdot A$ instantly executes a row swap.

## 7. Fundamental Laws of Matrix Algebra
When multiplying these matrices together (e.g., $E_{32} \cdot E_{21} \cdot A$), we must obey the laws of Matrix Algebra:
- **Non-Commutative:** Order matters! $AB \neq BA$. You cannot reverse the order of elimination steps.
- **Associative:** Grouping does not matter. $(AB)C = A(BC)$. This allows us to group all our Elimination matrices together into a single transformation matrix without breaking the logic.

## 8. Finding the Inverse: The Gauss-Jordan Method
If a matrix does not encounter a permanent failure (singular matrix) during elimination, it has an **Inverse** ($A^{-1}$). 
To find it algorithmically, we use the **Gauss-Jordan Method**:
1. Set up an Augmented Matrix with the Identity Matrix: $[A | I]$.
2. Perform row operations until the left side is transformed into the Identity Matrix $[I]$.
3. Because we perform the exact same operations on the right side, the right side will magically transform into the Inverse Matrix! The result is $[I | A^{-1}]$.
4. Mathematically, this tracks all the elimination steps ($E$) applied to $A$, proving that $E \cdot A = I$.
