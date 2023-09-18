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
from typing import TypeAlias, TypeVar

import nptyping as npt
import numpy as np

from ..tools import ScalarImageStack

M = TypeVar("M", bound=int)
N = TypeVar("N", bound=int)
D = TypeVar("D", bound=int)
K = TypeVar("K", bound=int)

VectorField: TypeAlias = npt.NDArray[npt.Shape["M,N,D"], npt.Floating]
MatrixField: TypeAlias = npt.NDArray[npt.Shape["M,N,D,D"], npt.Floating]


def getmatrices(image_stack: ScalarImageStack, ratio: float = 1.0) -> MatrixField:
    """
    Create a D x D hermitian matrix field form its channel decomposition
    :param image_stack: the stack of images of the channel decomposition.
    :param ratio: scaling controling the norm of the operator.
        If `ratio` = 1, the operator is unitary (its adjoint is its inverse).
    :return: the field of reconstructed Hermitian matrices.
    """
    k, m, n = image_stack.shape

    ratio /= np.sqrt(2)

    d = int(np.round(np.sqrt(k)))
    assert d * d == k, f"Expeceted k={k} to be the aqure of d={d}"

    matrix_field = np.zeros((m, n, d, d), dtype=complex)
    for k in range(d):
        matrix_field[:, :, k, k] = image_stack[k, :, :]

    k = d
    for i in range(d):
        for j in range(i + 1, d):
            matrix_field[:, :, i, j] += image_stack[k] * ratio
            matrix_field[:, :, j, i] += image_stack[k] * ratio
            k += 1
            matrix_field[:, :, i, j] += 1.0j * image_stack[k] * ratio
            matrix_field[:, :, j, i] -= 1.0j * image_stack[k] * ratio
            k += 1

    return matrix_field


def getmatrices_adj(matrix_field: MatrixField, ratio: float = 1.0) -> ScalarImageStack:
    """
    Adjoint of getmatrices
    """
    m, n, d, d = matrix_field.shape

    ratio *= np.sqrt(2)

    y = np.zeros((d**2, m, n))
    for k in range(d):
        y[k, :, :] = np.real(matrix_field[:, :, k, k])

    k = d
    for i in range(d):
        for j in range(i + 1, d):
            y[k, :, :] = np.real(matrix_field[:, :, i, j]) * ratio
            k = k + 1
            y[k, :, :] = np.imag(matrix_field[:, :, i, j]) * ratio
            k = k + 1

    return y


def getchannels(matrix_field: MatrixField, ratio: float = 1.0) -> ScalarImageStack:
    """
    Extract the channels of a DxD hermitian matrix field.
    :param matrix field: a field of Hermitian matrices.
    :param ratio: scaling controling the norm of the operator.
        If `ratio` = 1, the operator is unitary (its adjoint is its inverse).
    :return: the stack of images in the channel decomposition.
    """
    return getmatrices_adj(matrix_field, ratio=1 / ratio)
