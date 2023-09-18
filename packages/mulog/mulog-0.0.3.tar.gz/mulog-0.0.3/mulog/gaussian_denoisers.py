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
from typing import Callable, TypeAlias, TypeVar, Union

import bm3d
import numpy as np
from skimage.restoration import denoise_tv_chambolle
from strenum import StrEnum

from .tools import ScalarImage, ScalarImageStack

GaussianDenoiser: TypeAlias = Callable[[ScalarImageStack, float], ScalarImageStack]
TScalarImageOrStack = TypeVar(
    "TScalarImageOrStack", bound=Union[ScalarImage, ScalarImageStack]
)


def _run_autoscaled_denoiser(
    noisy_stack: TScalarImageOrStack,
    sig: float,
    denoiser: Callable[[ScalarImage, float], ScalarImage],
    max_optimal_sigma: float,
) -> TScalarImageOrStack:
    """
    Helper function to warp a 8bit denoiser to an unbounded denoiser
    """

    reshaped = False
    if noisy_stack.ndim == 2:
        noisy_stack = noisy_stack[np.newaxis]  # type: ignore
        reshaped = True

    min_value = float(np.min(noisy_stack))
    max_value = float(np.max(noisy_stack))
    d = noisy_stack.shape[0]

    tau = 255 * sig / (max_value - min_value)
    ratio = min(1.0, max_optimal_sigma / tau)
    autoscaled_noisy_stack = (
        255 * ratio * (noisy_stack - min_value) / (max_value - min_value)
    )
    result = np.stack(
        [
            denoiser(
                autoscaled_noisy_stack[k],
                ratio * tau,
            )
            / 255
            for k in range(d)
        ],
        axis=0,
    )
    result = (max_value - min_value) * result / ratio + min_value
    result[np.isnan(result)] = 0

    if reshaped:
        result = np.squeeze(result)

    return result  # type: ignore


def run_autoscaled_bm3d(
    noisy_stack: TScalarImageOrStack, sig: float
) -> TScalarImageOrStack:
    """
    Wrapper to the BM3D implementation of the authors. Unlike the native BM3D, this
    wrapper doesn't assume the image ranges between 0 and 255. Instead the image is
    rescaled to the 8bit range in an adaptive manner that aims at offering best
    performance. See:

        Y. Mäkinen, L. Azzari, A. Foi, "Collaborative Filtering of Correlated Noise:
        Exact Transform-Domain Variance for Improved Shrinkage and Patch Matching",
        IEEE Trans. Image Process., vol. 29, pp. 8339-8354, 2020.
        DOI: 10.1109/TIP.2020.3014721

    :param noisy_stack: a noisy image or a stack of noisy image.
    :param sig: the standard deviation of the Gaussian noise.
    :return: the BM3D solution.
    """

    return _run_autoscaled_denoiser(
        noisy_stack=noisy_stack,
        sig=sig,
        denoiser=lambda image, sig: (  # type: ignore
            255
            * bm3d.bm3d(
                image / 255,
                np.array([sig / 255]),
                "np",
            )
        ),
        max_optimal_sigma=40,
    )


def _run_stacked_denoiser(
    noisy_stack: TScalarImageOrStack,
    sig: float,
    denoiser: Callable[[ScalarImage, float], ScalarImage],
) -> TScalarImageOrStack:
    """
    Helper function to warp a scalar denoiser to a stack denoiser
    """
    if noisy_stack.ndim == 2:
        return denoiser(noisy_stack, sig)  # type: ignore
    elif noisy_stack.ndim == 3:
        return np.stack([denoiser(noisy, sig) for noisy in noisy_stack], axis=0)  # type: ignore
    else:
        raise Exception(f"Unexpected number of dimension {noisy_stack.ndim}")


def run_tv_denoising(noisy_stack: ScalarImageStack, sig: float) -> ScalarImageStack:
    """
    Wrapper to the TV implementation of Scikit-image.
    :param noisy_stack: a noisy image or a stack of noisy image.
    :param sig: the standard deviation of the Gaussian noise.
    :return: the BM3D solution.
    """
    return _run_stacked_denoiser(
        noisy_stack=noisy_stack,
        denoiser=lambda image, sigma: denoise_tv_chambolle(
            image,
            weight=np.sqrt(2) / 2 * sig,
            channel_axis=None,
            eps=1e-6,
            max_num_iter=1000,
        ),
        sig=sig,
    )


class PredefinedGaussianDenoiserNames(StrEnum):
    BM3D = "bm3d"
    TV = "tv"


PREDEFINED_GAUSSIAN_DENOISER_NAMES_TO_DENOISER: dict[
    PredefinedGaussianDenoiserNames, GaussianDenoiser
] = {
    PredefinedGaussianDenoiserNames.BM3D: run_autoscaled_bm3d,
    PredefinedGaussianDenoiserNames.TV: run_tv_denoising,
}
