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
from nptyping import Shape
import numpy as np
from scipy import special as sc

M = TypeVar("M", bound=int)
N = TypeVar("N", bound=int)
K = TypeVar("K", bound=int)

ScalarSignal: TypeAlias = npt.NDArray[Shape["N, ..."], npt.Floating]
ScalarImage: TypeAlias = npt.NDArray[Shape["M,N"], npt.Floating]
RGBImage: TypeAlias = (
    npt.NDArray[Shape["M,N,3"], npt.Floating] | npt.NDArray[Shape["M,N,3"], npt.Integer]
)
ScalarImageStack: TypeAlias = npt.NDArray[Shape["K,M,N"], npt.Floating]


def fftgrid(shape: tuple[int, ...]) -> list[npt.NDArray[Shape["K,..."], npt.Integer]]:
    """
    Generate a grid of frequency indices.
    :param shape: shape of the signal.
    :return: arrays of indices where each index is the frequency along the axis
        of the fft for the corresponding array (array 1 for axis 1, ...).
    """
    results = np.meshgrid(
        *[
            np.array(
                list(range(int(np.floor(n / 2)) + 1))
                + list(range(-int(np.ceil(n / 2)) + 1, 0))
            )
            for n in shape
        ],
        indexing="ij",
    )
    return results


class GaussianNoiseStdWithMadEstimationException(Exception):
    pass


def estimate_gaussian_noise_std_with_mad(image: ScalarImage) -> float:
    """
    Estimate the noise standard deviation of the image.
    """
    if image.shape[0] < 3 or image.shape[1] < 3:
        raise GaussianNoiseStdWithMadEstimationException(
            f"requires image to be at least 3x3 "
            f"but was {image.shape[0]}x{image.shape[1]}"
        )
    y = (image[:-1:2, :-1:2] - image[1::2, 1::2]) / np.sqrt(2)
    s = 1.4826 * np.median(np.abs(y - np.median(y)))
    return s


def estimate_gaussian_noise_std_with_mad_per_channel(
    image_stack: ScalarImageStack,
) -> list[float]:
    """
    Estimate the noise standard deviation on each channel of the stack.
    """
    return [estimate_gaussian_noise_std_with_mad(image) for image in image_stack]


def compute_fisher_tippet_noise_std(number_looks: float) -> float:
    """
    Compute theoretical standard deviation of Fisher-Tippet noise.
    """
    return float(np.sqrt(sc.polygamma(1.0, number_looks)))


def compute_fisher_tippet_noise_bias(number_looks: float) -> float:
    """
    Compute theoretical bias of Fisher-Tippet noise.
    """
    return sc.psi(number_looks) - np.log(number_looks)
