import numpy as np


def svd(A, k=None):
    """Perform SVD using the eigendecomposition of A*A^T and A^T*A"""
    U, S, Vt = svd_eigendecomposition(A)

    if k is not None:
        # Truncate to the top k singular values/vectors
        U = U[:, :k]
        S = S[:k]
        Vt = Vt[:k, :]

    # Reconstruct the compressed image
    comp_image = np.dot(U, np.dot(np.diag(S), Vt))

    return comp_image, U, S, Vt


def svd_eigendecomposition(A):
    """Compute A * A^T and A^T * A"""
    AAT = np.dot(A, A.T)
    ATA = np.dot(A.T, A)

    # Compute eigenvectors and eigenvalues of A * A^T
    eig_values_U, U = np.linalg.eigh(AAT)
    # Ensure non-negative singular values
    eig_values_U = np.sqrt(np.abs(eig_values_U))

    # Compute eigenvectors and eigenvalues of A^T * A
    eig_values_Vt, Vt = np.linalg.eigh(ATA)
    # Ensure non-negative singular values
    eig_values_Vt = np.sqrt(np.abs(eig_values_Vt))

    # Sort U, S, and Vt in descending order of singular values
    sort_indices_U = np.argsort(eig_values_U)[::-1]
    sort_indices_Vt = np.argsort(eig_values_Vt)[::-1]
    U = U[:, sort_indices_U]
    S = eig_values_U[sort_indices_U]
    Vt = Vt[:, sort_indices_Vt]

    return U, S, Vt
