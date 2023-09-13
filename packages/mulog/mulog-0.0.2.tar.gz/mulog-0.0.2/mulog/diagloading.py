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

from .hermitian_matrix_field import MatrixField
from .tools import fftgrid


def diagloading(image: MatrixField, number_looks: float) -> MatrixField:
    """
    Perform diagonal loading as described in [1]:

        Deledalle, C. A., Denis, L., Tabti, S., & Tupin, F. (2017). MuLoG,
        or how to apply Gaussian denoisers to multi-channel SAR speckle
        reduction?. IEEE Transactions on Image Processing, 26(9), 4389-4403.

    :param image: a field of Wishart matrices.
    :param number_looks: the number of looks (Wishart distribution parameter)
    :return: field of diagonal loaded positive Hermitian matrices.
    """

    m, n, d, d = image.shape
    r = max(min(number_looks, d), 1)

    x, y, i, j = fftgrid(shape=(m, n, d, d))
    tau = np.sqrt(2 * d / r / (4 * np.pi))

    i_0 = np.zeros_like(i)
    i_0[i == 0] = 1.0
    j_0 = np.zeros_like(j)
    j_0[j == 0] = 1.0

    kernel = i_0 * j_0 * np.exp(-(x**2 + y**2) / (2 * tau**2))  # Gaussian
    kernel = kernel / np.sum(kernel)
    image_conv = np.fft.ifftn(
        np.fft.fftn(image) * np.fft.fftn(kernel)
    )  # transfer function filter
    gamma = np.ones((m, n, d, d))
    gamma0 = np.ones((m, n, d, d))
    for i in range(d):
        for j in range(d):
            gamma[:, :, i, j] = np.abs(
                image_conv[:, :, i, j]
                / np.sqrt(image_conv[:, :, i, i] * image_conv[:, :, j, j])
            )
            gamma0[:, :, i, j] = np.abs(
                image[:, :, i, j] / np.sqrt(image[:, :, i, i] * image[:, :, j, j])
            )

    image = image * gamma / gamma0

    return image
