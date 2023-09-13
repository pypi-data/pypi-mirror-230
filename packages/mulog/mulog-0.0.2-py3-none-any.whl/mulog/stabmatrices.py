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

import numpy as np
from numpy import random as npr

from .hermitian_matrix_field import MatrixField


def stabmatrices(
    matrix_field: MatrixField,
    random_state: Optional[npr.RandomState] = None,
    epsilon: float = 1.0e-6,
) -> MatrixField:
    """
    Stabilize the input matrix in a way that
    * The modification is small: output ≈ input
    * The result does not have exact zero entries,
    * The reuslt does not have exact equal eigenvalues.

    Warning: using this function repeatidly will accumulate imprecisions
    that will quickly accumulate and leads to signficant errors.
    For instance:

         invmatrices(stabmatrices(invmatrices(stabmatrices(.)))) ≉ identitiy

    Try not to use that function too often then!

    :param matrix_field: a field of Hermitian non-negative definite matrices.
    :param random_state: the state of a random generator.
    :param epsilon: a small number controling the extent of the approximation.
    :return: a field of stabilized Hermitian non-negative definite matrices.
    """

    m, n, d, d = matrix_field.shape

    random_state = npr.RandomState(4242) if random_state is None else random_state

    positive_diag_min = np.full(matrix_field.shape[:2], fill_value=np.inf)
    for i in range(d):
        diag_i = np.real(matrix_field[:, :, i, i])
        positive_diag_i = diag_i > 0
        positive_diag_min[positive_diag_i] = np.minimum(
            positive_diag_min[positive_diag_i], diag_i[positive_diag_i]
        )

    positive_diag_min[positive_diag_min == 0] = epsilon

    stabilized_matrix_field = np.empty(matrix_field.shape, dtype=complex)
    for i in range(d):
        diag_i = np.real(matrix_field[:, :, i, i])
        positive_diag_i = diag_i > 0
        stabilized_matrix_field[positive_diag_i, i, i] = (
            1 + epsilon * (2 * random_state.rand(m, n) - 1)[positive_diag_i]
        ) * matrix_field[positive_diag_i, i, i]

        stabilized_matrix_field[~positive_diag_i, i, i] = (
            epsilon**2 * random_state.rand(m, n)[~positive_diag_i]
        ) * positive_diag_min[~positive_diag_i]

    for i in range(d):
        for j in range(i + 1, d):
            zeta = np.sqrt(
                stabilized_matrix_field[:, :, i, i]
                * stabilized_matrix_field[:, :, j, j]
            )
            stabilized_matrix_field[:, :, i, j] = np.abs(
                np.abs(matrix_field[:, :, i, j])
                + epsilon * zeta * (2 * random_state.rand(m, n) - 1)
            ) * np.exp(1.0j * np.angle(matrix_field[:, :, i, j]))
            stabilized_matrix_field[:, :, j, i] = np.conj(
                stabilized_matrix_field[:, :, i, j]
            )

    return stabilized_matrix_field
