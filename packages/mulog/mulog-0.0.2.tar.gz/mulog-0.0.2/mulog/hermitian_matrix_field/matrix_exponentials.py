"""
License

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software. You can use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty and the software's author, the holder of the
economic rights, and the successive licensors have only limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading, using, modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean that it is complicated to manipulate, and that also
therefore means that it is reserved for developers and experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and, more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Copyright Charles Deledalle (charles-alban.deledalle@math.u-bordeaux.fr)

List of Contributors:
  - Charles Deledalle (original version in Matlab)
  - Sébastien Mounier (translation in Python)
  - Cristiano Ulondu Mendes (bug fixes and improvements from MuLoG2022)

Scientific articles describing the method:

[1] Deledalle, C. A., Denis, L., Tabti, S., & Tupin, F. (2017). MuLoG,
    or how to apply Gaussian denoisers to multi-channel SAR speckle
    reduction?. IEEE Transactions on Image Processing, 26(9), 4389-4403.

[2] Deledalle, C. A., Denis, L., & Tupin, F. (2022). Speckle reduction
    in matrix-log domain for synthetic aperture radar imaging. Journal
    of Mathematical Imaging and Vision, 64(3), 298-320.
"""

from typing import Optional

from attr import define
import numpy as np

from .channel_decomposition import MatrixField
from .linear_algebra import (
    eigmatrices,
    mulmatrices,
    spfunmatrices,
)


@define
class ExpMatricesInternals:
    eigenvector_matrices: MatrixField
    eigenvector_adjoint_matrices: MatrixField
    eigenvalue_vectors: MatrixField
    exp_eigenvalue_vectors: MatrixField


def expmatrices_internals(
    matrix_field: MatrixField, return_internals: bool = False
) -> ExpMatricesInternals:
    (
        eigenvector_matrices,
        eigenvalue_vectors,
        eigenvector_adjoint_matrices,
    ) = eigmatrices(matrix_field)
    exp_eigenvalue_vectors = np.exp(eigenvalue_vectors)
    return ExpMatricesInternals(
        eigenvector_matrices=eigenvector_matrices,
        eigenvector_adjoint_matrices=eigenvector_adjoint_matrices,
        eigenvalue_vectors=eigenvalue_vectors,
        exp_eigenvalue_vectors=exp_eigenvalue_vectors,
    )


def expmatrices(
    matrix_field: MatrixField,
) -> MatrixField:
    """
    This function applies a the matrix exponential
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.
    """
    return spfunmatrices(matrix_field, lambda x: np.exp(x))


def expmatrices_with_internals(
    matrix_field: MatrixField,
) -> tuple[MatrixField, ExpMatricesInternals]:
    """
    Same as `expmatrices` but returns internals as well.
    """
    internals = expmatrices_internals(matrix_field=matrix_field)
    result = mulmatrices(
        internals.eigenvector_matrices
        * internals.exp_eigenvalue_vectors[:, :, np.newaxis, :],
        internals.eigenvector_adjoint_matrices,
    )

    return result, internals


def _expmatrices_get_matrix_f(
    matrix_g: MatrixField,
    matrix_j: MatrixField,
    matrix_ea: MatrixField,
    matrix_eb: MatrixField,
) -> MatrixField:
    m, n, d, d = matrix_g.shape
    matrix_f = np.empty((m, n, d, d), dtype=complex)
    for i in range(d):
        k = list(range(i)) + list(range(i + 1, d))
        phi = (
            2
            * (matrix_g[:, :, i, k] - (matrix_g[:, :, i, i])[:, :, None])
            * matrix_j[:, :, i, k]
        )
        matrix_f[:, :, i, i] = matrix_g[:, :, i, i] * matrix_eb[:, :, i, i] * matrix_ea[
            :, :, i, i
        ] + np.sum(
            phi * np.real(matrix_ea[:, :, i, k] * np.conj(matrix_eb[:, :, i, k])),
            axis=2,
        )
        for j in range(i + 1, d):
            phi = (matrix_g[:, :, j, :] - matrix_g[:, :, i, :]) * (
                (matrix_j[:, :, i, j])[:, :, None]
            )
            matrix_f[:, :, i, j] = np.sum(
                phi
                * (
                    matrix_eb[:, :, i, :] * np.conj(matrix_ea[:, :, j, :])
                    + matrix_ea[:, :, i, :] * np.conj(matrix_eb[:, :, j, :])
                ),
                2,
            )
            matrix_f[:, :, j, i] = np.conj(matrix_f[:, :, i, j])

    return matrix_f


def _expmatrices_get_matrix_g_and_j(
    eigenvalue_vector: MatrixField, exp_eigenvalue_vector: MatrixField
) -> tuple[MatrixField, MatrixField]:
    m, n, d = eigenvalue_vector.shape
    matrix_g = np.empty((m, n, d, d), dtype=float)
    matrix_j = np.empty((m, n, d, d), dtype=float)

    minimum_exp_eigenvalue_matrix = np.minimum(
        exp_eigenvalue_vector[:, :, :, np.newaxis],
        exp_eigenvalue_vector[:, :, np.newaxis, :],
    )
    maximum_exp_eigenvalue_matrix = np.maximum(
        exp_eigenvalue_vector[:, :, :, np.newaxis],
        exp_eigenvalue_vector[:, :, np.newaxis, :],
    )
    with np.errstate(divide="ignore"):
        matrix_j = 1 / np.real(
            eigenvalue_vector[:, :, np.newaxis, :]
            - eigenvalue_vector[:, :, :, np.newaxis]
        )
    with np.errstate(invalid="ignore"):
        matrix_g = (
            exp_eigenvalue_vector[:, :, np.newaxis, :]
            - exp_eigenvalue_vector[:, :, :, np.newaxis]
        ) * matrix_j

    matrix_g[np.isnan(matrix_g)] = 0  # In case of equals eigenvalues
    matrix_g[np.isinf(matrix_g)] = 0  # In case of equals eigenvalues
    min_mask = matrix_g < minimum_exp_eigenvalue_matrix
    matrix_g[min_mask] = minimum_exp_eigenvalue_matrix[min_mask]
    max_mask = matrix_g > maximum_exp_eigenvalue_matrix
    matrix_g[max_mask] = maximum_exp_eigenvalue_matrix[max_mask]
    return matrix_g, matrix_j


@define
class ExpMatricesDirectinalDerivativeInternals(ExpMatricesInternals):
    eigen_direction: MatrixField
    matrix_g: MatrixField
    matrix_j: MatrixField


def expmatrices_directional_derivative_from_internals(
    precomputed_internals: ExpMatricesInternals, direction: MatrixField
) -> MatrixField:
    eigenvector_matrices = precomputed_internals.eigenvector_matrices
    eigenvector_adjoint_matrices = precomputed_internals.eigenvector_adjoint_matrices
    eigenvalue_vectors = precomputed_internals.eigenvalue_vectors
    exp_eigenvalue_vectors = precomputed_internals.exp_eigenvalue_vectors

    if isinstance(precomputed_internals, ExpMatricesDirectinalDerivativeInternals):
        matrix_g = precomputed_internals.matrix_g
        matrix_j = precomputed_internals.matrix_j
        eigen_direction = precomputed_internals.eigen_direction
    else:
        matrix_g, matrix_j = _expmatrices_get_matrix_g_and_j(
            eigenvalue_vectors, exp_eigenvalue_vectors
        )
        eigen_direction = mulmatrices(
            mulmatrices(eigenvector_adjoint_matrices, direction), eigenvector_matrices
        )

    result = mulmatrices(
        mulmatrices(eigenvector_matrices, matrix_g * eigen_direction),
        eigenvector_adjoint_matrices,
    )

    return result


def expmatrices_directional_derivative_from_internals_with_internals(
    precomputed_internals: ExpMatricesInternals, direction: MatrixField
) -> tuple[MatrixField, ExpMatricesDirectinalDerivativeInternals]:
    eigenvector_matrices = precomputed_internals.eigenvector_matrices
    eigenvector_adjoint_matrices = precomputed_internals.eigenvector_adjoint_matrices
    eigenvalue_vectors = precomputed_internals.eigenvalue_vectors
    exp_eigenvalue_vectors = precomputed_internals.exp_eigenvalue_vectors

    if isinstance(precomputed_internals, ExpMatricesDirectinalDerivativeInternals):
        matrix_g = precomputed_internals.matrix_g
        matrix_j = precomputed_internals.matrix_j
        eigen_direction = precomputed_internals.eigen_direction
    else:
        matrix_g, matrix_j = _expmatrices_get_matrix_g_and_j(
            eigenvalue_vectors, exp_eigenvalue_vectors
        )
        eigen_direction = mulmatrices(
            mulmatrices(eigenvector_adjoint_matrices, direction), eigenvector_matrices
        )

    result = mulmatrices(
        mulmatrices(eigenvector_matrices, matrix_g * eigen_direction),
        eigenvector_adjoint_matrices,
    )

    return (
        result,
        ExpMatricesDirectinalDerivativeInternals(
            eigenvector_matrices=eigenvector_matrices,
            eigenvector_adjoint_matrices=eigenvector_adjoint_matrices,
            eigenvalue_vectors=eigenvalue_vectors,
            exp_eigenvalue_vectors=exp_eigenvalue_vectors,
            eigen_direction=eigen_direction,
            matrix_g=matrix_g,
            matrix_j=matrix_j,
        ),
    )


def expmatrices_directional_derivative(
    matrix_field: MatrixField,
    direction: MatrixField,
    precomputed_internals: Optional[ExpMatricesInternals] = None,
) -> MatrixField:
    """
    This function applies a the matrix exponential
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.
    """

    if precomputed_internals is None:
        precomputed_internals = expmatrices_internals(matrix_field)
    return expmatrices_directional_derivative_from_internals(
        precomputed_internals=precomputed_internals, direction=direction
    )


def expmatrices_directional_derivative_with_internals(
    matrix_field: MatrixField,
    direction: MatrixField,
    precomputed_internals: Optional[ExpMatricesInternals] = None,
) -> tuple[MatrixField, ExpMatricesDirectinalDerivativeInternals]:
    """
    This function applies a the matrix exponential
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.
    """

    if precomputed_internals is None:
        precomputed_internals = expmatrices_internals(matrix_field)
    return expmatrices_directional_derivative_from_internals_with_internals(
        precomputed_internals=precomputed_internals, direction=direction
    )


@define
class ExpMatricesSecondDirectinalDerivativeInternals(ExpMatricesInternals):
    eigen_direction_a: MatrixField
    eigen_direction_b: MatrixField
    matrix_g: MatrixField
    matrix_j: MatrixField
    matrix_f: MatrixField


def expmatrices_second_directional_derivative_internals_from_internals(
    precomputed_internals: ExpMatricesDirectinalDerivativeInternals,
    direction_b: MatrixField,
) -> ExpMatricesSecondDirectinalDerivativeInternals:
    eigenvector_matrices = precomputed_internals.eigenvector_matrices
    eigenvector_adjoint_matrices = precomputed_internals.eigenvector_adjoint_matrices
    eigenvalue_vectors = precomputed_internals.eigenvalue_vectors
    exp_eigenvalue_vectors = precomputed_internals.exp_eigenvalue_vectors
    matrix_g = precomputed_internals.matrix_g
    matrix_j = precomputed_internals.matrix_j

    eigen_direction_a = precomputed_internals.eigen_direction
    eigen_direction_b = mulmatrices(
        mulmatrices(eigenvector_adjoint_matrices, direction_b), eigenvector_matrices
    )
    matrix_f = _expmatrices_get_matrix_f(
        matrix_g, matrix_j, eigen_direction_a, eigen_direction_b
    )
    return ExpMatricesSecondDirectinalDerivativeInternals(
        eigenvector_matrices=eigenvector_matrices,
        eigenvector_adjoint_matrices=eigenvector_adjoint_matrices,
        eigenvalue_vectors=eigenvalue_vectors,
        exp_eigenvalue_vectors=exp_eigenvalue_vectors,
        eigen_direction_a=eigen_direction_a,
        eigen_direction_b=eigen_direction_b,
        matrix_g=matrix_g,
        matrix_j=matrix_j,
        matrix_f=matrix_f,
    )


def expmatrices_second_directional_derivative(
    matrix_field: MatrixField,
    direction_a: MatrixField,
    direction_b: MatrixField,
    precomputed_internals: Optional[ExpMatricesDirectinalDerivativeInternals] = None,
) -> MatrixField:
    """
    This function applies a the matrix exponential
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.
    """

    M, N, D, D = direction_b.shape
    if precomputed_internals is None:
        (
            eigenvector_matrices,
            eigenvalue_vectors,
            eigenvector_adjoint_matrices,
        ) = eigmatrices(matrix_field)
        exp_eigenvalue_vectors = np.exp(eigenvalue_vectors)
        matrix_g, matrix_j = _expmatrices_get_matrix_g_and_j(
            eigenvalue_vectors, exp_eigenvalue_vectors
        )
        eigen_direction_a = mulmatrices(
            mulmatrices(eigenvector_adjoint_matrices, direction_a), eigenvector_matrices
        )
        precomputed_internals = ExpMatricesDirectinalDerivativeInternals(
            eigenvector_matrices=eigenvector_matrices,
            eigenvector_adjoint_matrices=eigenvector_adjoint_matrices,
            eigenvalue_vectors=eigenvalue_vectors,
            exp_eigenvalue_vectors=exp_eigenvalue_vectors,
            eigen_direction=eigen_direction_a,
            matrix_g=matrix_g,
            matrix_j=matrix_j,
        )

    internals = expmatrices_second_directional_derivative_internals_from_internals(
        precomputed_internals=precomputed_internals, direction_b=direction_b
    )

    return mulmatrices(
        mulmatrices(internals.eigenvector_matrices, internals.matrix_f),
        internals.eigenvector_adjoint_matrices,
    )
