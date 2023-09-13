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

import numpy as np

from .hermitian_matrix_field import MatrixField, eigmatrices, mulmatrices


def condloading(image: MatrixField, inverse_condition_number: float) -> MatrixField:
    """
    Perform conditioning loading as described in [2]:

        Deledalle, C. A., Denis, L., & Tupin, F. (2022). Speckle reduction
        in matrix-log domain for synthetic aperture radar imaging. Journal
        of Mathematical Imaging and Vision, 64(3), 298-320.

    :param image: a field of Hermitian non-negative definite matrices
    :param inverse_condition_number: the prescribed minimum inverse of the
        condition number of the resulting matrices
    :result: the field of conditioned Hermitian positive definite matrices
    """

    m, n, d, d = image.shape

    assert 0 < inverse_condition_number <= 1

    if d == 1:
        return image.copy()

    (
        eigenvector_matrices,
        eigenvalue_vectors,
        eigenvector_adjoint_matrices,
    ) = eigmatrices(image)

    mask = eigenvalue_vectors > 0
    if np.any(mask):
        eigenvalue_vectors[~mask] = min(eigenvalue_vectors[mask])
    else:
        assert ValueError("Something doesn't make sense")

    max_eigenvalues = np.max(eigenvalue_vectors, axis=2)[:, :, np.newaxis]
    min_eigenvalues = np.min(eigenvalue_vectors, axis=2)[:, :, np.newaxis]
    cond = np.maximum(inverse_condition_number, min_eigenvalues / max_eigenvalues)
    gap = max_eigenvalues - min_eigenvalues
    gap[gap <= 0.0] = 1
    eigenvalue_vectors = (
        (eigenvalue_vectors - min_eigenvalues) / gap
    ) * max_eigenvalues * (1 - cond) + max_eigenvalues * cond
    return mulmatrices(
        eigenvector_matrices * eigenvalue_vectors[:, :, np.newaxis, :],
        eigenvector_adjoint_matrices,
    )
