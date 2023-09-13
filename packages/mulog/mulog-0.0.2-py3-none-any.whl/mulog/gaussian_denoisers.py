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
from typing import TypeVar, Union

import bm3d
import numpy as np

from .tools import ScalarImage, ScalarImageStack

TScalarImageOrStack = TypeVar(
    "TScalarImageOrStack", bound=Union[ScalarImage, ScalarImageStack]
)


def run_autoscaled_bm3d(
    noisy_image: TScalarImageOrStack, sig: float
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

    :param noisy_image: a noisy image or a stack of noisy image.
    :param sig: the standard deviation of the Gaussian noise.
    :return: the BM3D solution.
    """

    reshaped = False
    if noisy_image.ndim == 2:
        noisy_image = noisy_image[np.newaxis]  # type: ignore
        reshaped = True

    result = np.zeros_like(noisy_image)
    min_value = np.min(noisy_image)
    max_value = np.max(noisy_image)
    d = noisy_image.shape[0]

    for k in range(d):
        tau = 255 * sig / (max_value - min_value)
        if tau > 40:
            ratio = 40 / tau
        else:
            ratio = 1

        result[k] = bm3d.bm3d(
            ratio * (noisy_image[k] - min_value) / (max_value - min_value),
            np.array([ratio * tau / 255]),
            "np",
        )
        result[k] = (max_value - min_value) * result[k] / ratio + min_value
    result[np.isnan(result)] = 0

    if reshaped:
        result = np.squeeze(result)

    return result  # type: ignore
