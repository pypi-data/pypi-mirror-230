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

from typing import Callable, Optional, TypeVar

from attr import define
import nptyping as npt
import numpy as np

from ..tools import (
    ScalarImage,
    ScalarImageStack,
    compute_fisher_tippet_noise_std,
    estimate_gaussian_noise_std_with_mad_per_channel,
)
from .channel_decomposition import (
    MatrixField,
    getchannels,
    getmatrices,
    getmatrices_adj,
)
from .linear_algebra import logmatrices
from .matrix_exponentials import expmatrices

K = TypeVar("K", bound=int)


def _applyr(x: ScalarImageStack, f: Callable) -> ScalarImageStack:
    k, m, n = x.shape
    return f(x.reshape((k, -1))).reshape((-1, m, n))


@define
class LogChannelPCA:
    rotation: npt.NDArray[npt.Shape["K,K"], npt.Floating]
    translation: npt.NDArray[npt.Shape["K"], npt.Floating]
    scalings: npt.NDArray[npt.Shape["K"], npt.Floating]
    noise_standard_deviations: npt.NDArray[npt.Shape["K"], npt.Floating]
    _whitening: Optional[npt.NDArray[npt.Shape["K,K"], npt.Floating]] = None

    @property
    def whitening(self) -> npt.NDArray[npt.Shape["K,K"], npt.Floating]:
        if self._whitening is None:
            self._whitening = self.rotation @ np.diag(self.noise_standard_deviations)
        return self._whitening

    def omega(self, log_channels: ScalarImageStack) -> MatrixField:
        return getmatrices(
            _applyr(
                log_channels, lambda z: self.whitening @ z + self.translation[:, None]
            )
        )

    def theta(self, matrix_field: MatrixField) -> ScalarImageStack:
        return _applyr(getmatrices_adj(matrix_field), lambda z: self.whitening.T @ z)

    def theta_adjoint(self, log_channels: ScalarImageStack) -> MatrixField:
        return getmatrices(_applyr(log_channels, lambda z: self.whitening @ z))


def covariance_matrix_field_to_log_channels(
    matrix_field: MatrixField, number_looks: float
) -> tuple[ScalarImageStack, LogChannelPCA]:
    """
    Extract log channels from a given covariance matrix field
    """
    m, n, d, d = matrix_field.shape
    k = d**2

    alpha = getchannels(logmatrices(matrix_field))
    alpha = alpha.reshape((k, -1))

    translation = np.mean(alpha, axis=1)

    residue = alpha - translation[:, np.newaxis]

    rotation, scalings, _ = np.linalg.svd(residue / np.sqrt(m * n), full_matrices=False)

    whitened_residue = rotation.T @ residue

    whitened_residue = whitened_residue.reshape((-1, m, n))

    if d == 1:
        noise_standard_deviations = np.array(
            [compute_fisher_tippet_noise_std(number_looks)]
        )
    else:
        noise_standard_deviations = np.array(
            estimate_gaussian_noise_std_with_mad_per_channel(whitened_residue)
        )
    if not np.any(noise_standard_deviations > 0):
        assert Exception
    else:
        noise_standard_deviations[noise_standard_deviations == 0] = np.min(
            noise_standard_deviations[noise_standard_deviations > 0]
        )

    image_stack = (
        whitened_residue / noise_standard_deviations[:, np.newaxis, np.newaxis]
    )

    return (
        image_stack,
        LogChannelPCA(
            rotation=rotation,
            translation=translation,
            scalings=scalings,
            noise_standard_deviations=noise_standard_deviations,
        ),
    )


def log_channels_to_covariance_matrix_field(
    image_stack: ScalarImageStack, pca: LogChannelPCA
) -> MatrixField:
    """
    Reconstruct a covariance matrix field from the given log channels
    """
    return expmatrices(pca.omega(image_stack))
