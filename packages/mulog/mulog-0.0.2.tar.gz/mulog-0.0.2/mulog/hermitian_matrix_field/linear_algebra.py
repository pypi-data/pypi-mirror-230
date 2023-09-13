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

from typing import Callable

import numpy as np

from ..tools import ScalarImage
from .channel_decomposition import MatrixField, VectorField


def adjmatrices(matrix_field: MatrixField) -> MatrixField:
    """
    Get the adjoint of all matrices of the field
    """
    return np.conj(np.transpose(matrix_field, axes=(0, 1, 3, 2)))


def mulmatrices(
    matrix_field_1: MatrixField, matrix_field_2: MatrixField
) -> MatrixField:
    return np.matmul(matrix_field_1, matrix_field_2)


def tracematrices(matrix_field: MatrixField) -> ScalarImage:
    """
    Compute the trace of all matrices of the field
    """
    d = matrix_field.shape[-1]
    return np.sum([matrix_field[:, :, k, k] for k in range(d)], axis=0)


def eigmatrices(
    matrix_field: MatrixField,
) -> tuple[MatrixField, MatrixField, MatrixField]:
    """
    This function perform the eigenvalues/eigenvectors decomposition of a field
    of hermitian matrices. A detailed description is given in

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.

    Warning: if the matrices have zero entries or equal eigenvalues,
    the function may crash or produce an unexpected result.
    Please use stabmatrices on C, prior to calling this function,
    in order to avoid such numerical issues.
    """

    m, n, d, d = matrix_field.shape

    eigen_value_vectors = np.zeros((m, n, d), dtype=float)
    eigen_vector_matrices = np.zeros((m, n, d, d), dtype=complex)

    if d == 1:
        eigen_vector_matrices[:] = 1.0
        eigen_value_vectors = np.real(matrix_field[:, :, :, 0])
    elif d == 2:  # apply formula for 2 x 2 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 1, 0]

        # compute relevant quantity
        delta = np.sqrt(np.maximum(4 * np.abs(c) ** 2 + (a - b) ** 2, 0.0))

        # compute eigenvalues
        eigen_value_vectors[:, :, 0] = np.real((a + b + delta) / 2)
        eigen_value_vectors[:, :, 1] = np.real((a + b - delta) / 2)

        # compute eigenvectors
        u11 = (a - b + delta) / 2
        u21 = (a - b - delta) / 2
        n1 = np.sqrt(np.maximum(np.abs(u11) ** 2 + np.abs(c) ** 2, 0.0))
        n2 = np.sqrt(np.maximum(np.abs(u21) ** 2 + np.abs(c) ** 2, 0.0))

        eigen_vector_matrices[:, :, 0, 0] = u11 / n1
        eigen_vector_matrices[:, :, 1, 0] = c / n1

        eigen_vector_matrices[:, :, 0, 1] = u21 / n2
        eigen_vector_matrices[:, :, 1, 1] = c / n2

    elif d == 3:  # aply formula for 3 x 3 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 2, 2].real
        d = matrix_field[:, :, 1, 0]
        e = matrix_field[:, :, 2, 1]
        f = matrix_field[:, :, 2, 0]

        # compute relevant quantities
        x1 = (
            a**2
            + b**2
            + c**2
            - a * b
            - a * c
            - b * c
            + 3
            * (
                np.real(d) ** 2
                + np.imag(d) ** 2
                + np.real(e) ** 2
                + np.imag(e) ** 2
                + np.real(f) ** 2
                + np.imag(f) ** 2
            )
        )
        x2 = (
            -(2 * a - b - c) * (2 * b - a - c) * (2 * c - a - b)
            + 9
            * (
                (2 * c - a - b) * (np.real(d) ** 2 + np.imag(d) ** 2)
                + (2 * b - a - c) * (np.real(f) ** 2 + np.imag(f) ** 2)
                + (2 * a - b - c) * (np.real(e) ** 2 + np.imag(e) ** 2)
            )
            - 54
            * (
                (np.real(d) * np.real(e) - np.imag(d) * np.imag(e)) * np.real(f)
                + (np.real(d) * np.imag(e) + np.imag(d) * np.real(e)) * np.imag(f)
            )
        )
        phi = (
            np.arctan(np.sqrt(np.maximum(4 * (x1**3) - x2**2, 0.0)) / x2)
            + np.abs(np.sign(x2)) * (1 - np.sign(x2)) / 2 * np.pi
        )
        x1 = np.sqrt(np.maximum(x1, 0.0))
        lambda1 = np.real((1 / 3) * (a + b + c - 2 * x1 * np.cos(phi / 3)))
        lambda2 = np.real((1 / 3) * (a + b + c + 2 * x1 * np.cos((phi - np.pi) / 3)))
        lambda3 = np.real((1 / 3) * (a + b + c + 2 * x1 * np.cos((phi + np.pi) / 3)))

        m1 = (d * (c - lambda1) - np.conj(e) * f) / (f * (b - lambda1) - d * e)
        m2 = (d * (c - lambda2) - np.conj(e) * f) / (f * (b - lambda2) - d * e)
        m3 = (d * (c - lambda3) - np.conj(e) * f) / (f * (b - lambda3) - d * e)

        v11 = lambda1 - c - e * m1
        v21 = lambda2 - c - e * m2
        v31 = lambda3 - c - e * m3
        m1 *= f
        m2 *= f
        m3 *= f
        n1 = np.sqrt(
            np.maximum(np.abs(v11) ** 2 + np.abs(m1) ** 2 + np.abs(f) ** 2, 0.0)
        )
        n2 = np.sqrt(
            np.maximum(np.abs(v21) ** 2 + np.abs(m2) ** 2 + np.abs(f) ** 2, 0.0)
        )
        n3 = np.sqrt(
            np.maximum(np.abs(v31) ** 2 + np.abs(m3) ** 2 + np.abs(f) ** 2, 0.0)
        )

        # compute eigenvalues
        eigen_value_vectors[:, :, 0] = lambda1
        eigen_value_vectors[:, :, 1] = lambda2
        eigen_value_vectors[:, :, 2] = lambda3

        # compute eigenvectors
        eigen_vector_matrices[:, :, 0, 0] = v11 / n1
        eigen_vector_matrices[:, :, 1, 0] = m1 / n1
        eigen_vector_matrices[:, :, 2, 0] = f / n1
        eigen_vector_matrices[:, :, 0, 1] = v21 / n2
        eigen_vector_matrices[:, :, 1, 1] = m2 / n2
        eigen_vector_matrices[:, :, 2, 1] = f / n2
        eigen_vector_matrices[:, :, 0, 2] = v31 / n3
        eigen_vector_matrices[:, :, 1, 2] = m3 / n3
        eigen_vector_matrices[:, :, 2, 2] = f / n3

    else:  # no formula ... use python function
        eigen_value_vectors, eigen_vector_matrices = np.linalg.eig(matrix_field)

    eigen_vector_adj_matrices = adjmatrices(eigen_vector_matrices)

    return eigen_vector_matrices, eigen_value_vectors, eigen_vector_adj_matrices


def spfunmatrices(
    matrix_field: MatrixField, func: Callable[[VectorField], VectorField]
) -> MatrixField:
    """
    This function applies a matrix-valued spectral function
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.
    It applies `func` to the eigenvalues of the matrix field
    and reconstruct a matrix field with the same eigenvectors.
    A detailed description is given in

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.

    Warning: if the matrices have zero entries or equal eigenvalues,
    the function may crash or produce an unexpected result.
    Please use stabmatrices, prior to calling this function,
    in order to avoid such numerical issues.

    :param matrix_field: a field of Hermitian matrices.
    :param func: a scalar function to apply to the vector field of eigen values.
    :return: the field of mapped Hermitian matrices.
    """

    result = np.empty_like(matrix_field)

    m, n, d, d = result.shape
    if d == 1:
        result = func(matrix_field)

    elif d == 2:  # apply formula for 2 x 2 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 1, 0]

        # compute relevant quantity
        delta = np.sqrt(np.maximum(4 * np.abs(c) ** 2 + (a - b) ** 2, 0.0))

        # compute and update eigenvalues
        l1_l2 = func(
            np.stack(
                (
                    (a + b + delta) / 2,
                    (a + b - delta) / 2,
                ),
                axis=-1,
            )
        )
        l1 = l1_l2[..., 0]
        l2 = l1_l2[..., 1]

        # build updated matrix
        result[:, :, 0, 0] = (
            (1) * ((a - b + delta) * l1 - (a - b - delta) * l2) / (2 * delta)
        )
        result[:, :, 1, 1] = ((b - a + delta) * l1 - (b - a - delta) * l2) / (2 * delta)
        result[:, :, 1, 0] = c * (l1 - l2) / delta
        result[:, :, 0, 1] = np.conj(result[:, :, 1, 0])

    elif d == 3:  # apply formula for 3 x 3 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 2, 2].real
        d = matrix_field[:, :, 1, 0]
        e = matrix_field[:, :, 2, 1]
        f = matrix_field[:, :, 2, 0]

        # compute relevant quantities
        x1 = (
            a**2
            + b**2
            + c**2
            - a * b
            - a * c
            - b * c
            + 3
            * (
                np.real(d) ** 2
                + np.imag(d) ** 2
                + np.real(e) ** 2
                + np.imag(e) ** 2
                + np.real(f) ** 2
                + np.imag(f) ** 2
            )
        )
        x2 = (
            -(2 * a - b - c) * (2 * b - a - c) * (2 * c - a - b)
            + 9
            * (
                (2 * c - a - b) * (np.real(d) ** 2 + np.imag(d) ** 2)
                + (2 * b - a - c) * (np.real(f) ** 2 + np.imag(f) ** 2)
                + (2 * a - b - c) * (np.real(e) ** 2 + np.imag(e) ** 2)
            )
            - 54
            * (
                (np.real(d) * np.real(e) - np.imag(d) * np.imag(e)) * np.real(f)
                + (np.real(d) * np.imag(e) + np.imag(d) * np.real(e)) * np.imag(f)
            )
        )
        with np.errstate(invalid="ignore"):
            phi = (
                np.arctan(np.sqrt(np.maximum(4 * x1**3 - x2**2, 0)) / x2)
                + np.abs(np.sign(x2)) * (1 - np.sign(x2)) / 2 * np.pi
            )
        x1 = np.sqrt(np.maximum(x1, 0.0))
        lambda1 = 1 / 3 * (a + b + c - 2 * x1 * np.cos(phi / 3))
        lambda2 = 1 / 3 * (a + b + c + 2 * x1 * np.cos((phi - np.pi) / 3))
        lambda3 = 1 / 3 * (a + b + c + 2 * x1 * np.cos((phi + np.pi) / 3))

        m1 = (d * (c - lambda1) - np.conj(e) * f) / (f * (b - lambda1) - d * e)
        m2 = (d * (c - lambda2) - np.conj(e) * f) / (f * (b - lambda2) - d * e)
        m3 = (d * (c - lambda3) - np.conj(e) * f) / (f * (b - lambda3) - d * e)
        v11 = (lambda1 - c - e * m1) / f
        v21 = (lambda2 - c - e * m2) / f
        v31 = (lambda3 - c - e * m3) / f
        n1 = np.abs(v11) ** 2 + np.abs(m1) ** 2 + 1
        n2 = np.abs(v21) ** 2 + np.abs(m2) ** 2 + 1
        n3 = np.abs(v31) ** 2 + np.abs(m3) ** 2 + 1

        # compute and update 'tilde' eigenvalues
        lambda1_lambda2_lambda3 = func(np.stack((lambda1, lambda2, lambda3), axis=-1))
        lambda1 = lambda1_lambda2_lambda3[..., 0] / n1
        lambda2 = lambda1_lambda2_lambda3[..., 1] / n2
        lambda3 = lambda1_lambda2_lambda3[..., 2] / n3

        # build updated matrix
        result[:, :, 0, 0] = (
            lambda1 * (np.real(v11) ** 2 + np.imag(v11) ** 2)
            + lambda2 * (np.real(v21) ** 2 + np.imag(v21) ** 2)
            + lambda3 * (np.real(v31) ** 2 + np.imag(v31) ** 2)
        )

        result[:, :, 1, 1] = (
            lambda1 * (np.real(m1) ** 2 + np.imag(m1) ** 2)
            + lambda2 * (np.real(m2) ** 2 + np.imag(m2) ** 2)
            + lambda3 * (np.real(m3) ** 2 + np.imag(m3) ** 2)
        )

        result[:, :, 2, 2] = lambda1 + lambda2 + lambda3
        result[:, :, 1, 0] = (
            lambda1 * m1 * np.conj(v11)
            + lambda2 * m2 * np.conj(v21)
            + lambda3 * m3 * np.conj(v31)
        )
        result[:, :, 2, 1] = (
            lambda1 * np.conj(m1) + lambda2 * np.conj(m2) + lambda3 * np.conj(m3)
        )
        result[:, :, 2, 0] = (
            lambda1 * np.conj(v11) + lambda2 * np.conj(v21) + lambda3 * np.conj(v31)
        )
        result[:, :, 0, 1] = np.conj(result[:, :, 1, 0])
        result[:, :, 0, 2] = np.conj(result[:, :, 2, 0])
        result[:, :, 1, 2] = np.conj(result[:, :, 2, 1])

    else:  # no formula... use numpy function
        eigenvalues, eigenvectors = np.linalg.eig(matrix_field)
        result = np.matmul(
            eigenvectors * func(eigenvalues)[:, :, np.newaxis, :],
            adjmatrices(eigenvectors),
        )

    result = (result + adjmatrices(result)) / 2

    return result


def spfunpdmatrices(
    matrix_field: MatrixField, func: Callable[[VectorField], VectorField]
) -> MatrixField:
    """
    Same as `spfunmatrices` but assumes the matrices to be Hermition positive-definite.

    Warning: if the matrices in input are not hermitian positive definite, the output
    of this function will be nonsense.

    :param matrix_field: a field of hermitian postive definite matrices
    :return: the log matrices of each of the input matrices
    """
    return spfunmatrices(
        matrix_field,
        lambda x: func(np.maximum(x, np.max(x, axis=-1)[:, :, np.newaxis] * 1e-6)),
    )


def logmatrices(matrix_field: MatrixField) -> MatrixField:
    """
    Compute the logarithm of all the matrices of the field.
    :param matrix_field: a field of hermitian postive definite matrices
    :return: the log matrices of each of the input matrices
    """
    return spfunpdmatrices(matrix_field, np.log)


def spfunscalars(
    matrix_field: MatrixField, func: Callable[[VectorField], VectorField]
) -> VectorField:
    """
    This function applies a matrix-valued spectral function
    to a 2d hermitian matrix field (an image of matrices).
    Is is optimized for hermitian matrices of size up to 3x3.
    It applies `func` to the eigenvalues of the matrix field
    and reconstruct a vector field with these mapped eigenvalues.
    A detailed description is given in

       Deledalle, C.A., Denis, L., Tabti, S. and Tupin, F., 2017.
       Closed-form expression of the eigen decomposition
       of 2 x 2 and 3 x 3 Hermitian matrices

    Warning: if the matrices in input are not hermitian, the output
    of this function will be nonsense.

    Warning: if the matrices have zero entries or equal eigenvalue,
    the function may crash or produce an unexpected result.
    Please use stabmatrices on C, prior to calling this function,
    in oreder to avoid such numerical issues.

    :param matrix_field: a field of Hermitian matrices.
    :param func: a scalar function to apply to the vector field of eigen values.
    :return: the vector field of mapped eigen values.
    """

    M, N, D, D = matrix_field.shape
    result = np.zeros_like(matrix_field)
    if D == 1:
        result = func(matrix_field)[..., -1]

    elif D == 2:  # apply formula for 2 x 2 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 1, 0]

        # compute relevant quantity
        delta = np.sqrt(np.maximum(4 * np.abs(c) ** 2 + (a - b) ** 2, 0.0))

        # compute and update eigenvalues
        l1 = (a + b + delta) / 2
        l2 = (a + b - delta) / 2

        result = func(np.stack((l1, l2), axis=-1))

    elif D == 3:  # apply formula for 3 x 3 matrices
        # extract channels
        a = matrix_field[:, :, 0, 0].real
        b = matrix_field[:, :, 1, 1].real
        c = matrix_field[:, :, 2, 2].real
        d = matrix_field[:, :, 1, 0]
        e = matrix_field[:, :, 2, 1]
        f = matrix_field[:, :, 2, 0]

        # compute relevant quantitties
        x1 = (
            a**2
            + b**2
            + c**2
            - a * b
            - a * c
            - b * c
            + 3
            * (
                np.real(d) ** 2
                + np.imag(d) ** 2
                + np.real(e) ** 2
                + np.imag(e) ** 2
                + np.real(f) ** 2
                + np.imag(f) ** 2
            )
        )
        x2 = (
            -(2 * a - b - c) * (2 * b - a - c) * (2 * c - a - b)
            + 9
            * (
                (2 * c - a - b) * (np.real(d) ** 2 + np.imag(d) ** 2)
                + (2 * b - a - c) * (np.real(f) ** 2 + np.imag(f) ** 2)
                + (2 * a - b - c) * (np.real(e) ** 2 + np.imag(e) ** 2)
            )
            - 54
            * (
                (np.real(d) * np.real(e) - np.imag(d) * np.imag(e)) * np.real(f)
                + (np.real(d) * np.imag(e) + np.imag(d) * np.real(e)) * np.imag(f)
            )
        )
        phi = (
            np.arctan(np.sqrt(np.maximum(4 * x1**3 - x2**2, 0.0)) / x2)
            + np.abs(np.sign(x2)) * (1 - np.sign(x2)) / 2 * np.pi
        )
        x1 = np.sqrt(np.maximum(x1, 0.0))
        lambda1 = 1 / 3 * (a + b + c - 2 * np.cos(phi / 3))
        lambda2 = 1 / 3 * (a + b + c + 2 * np.cos((phi - np.pi) / 3))
        lambda3 = 1 / 3 * (a + b + c + 2 * np.cos((phi + np.pi) / 3))

        result = func(np.stack((lambda1, lambda2, lambda3), axis=-1))

    else:  # no formula ... use python function
        eigenvalues, _ = np.linalg.eig(matrix_field)
        result = func(eigenvalues)

    return result
