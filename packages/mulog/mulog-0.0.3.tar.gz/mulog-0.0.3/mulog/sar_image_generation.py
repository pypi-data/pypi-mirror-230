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

from typing import Optional, TypeVar

import numpy as np

from .condloading import condloading
from .hermitian_matrix_field import MatrixField, mulmatrices, spfunpdmatrices
from .mulog_algorithm import TSARImage
from .stabmatrices import stabmatrices
from .tools import RGBImage

M = TypeVar("M", bound=int)
N = TypeVar("N", bound=int)


def generate_mondrian_image() -> RGBImage:
    """
    Generate a synthetic image that looks like a Mondrian's painting.
    :return: an RGB image.
    """
    result = np.empty((50, 101, 3), dtype=np.uint8)
    result[:25, :75, :] = np.array([255, 1, 0])
    result[:25, 75:, :] = np.array([1, 255, 1])
    result[25:, :50, :] = np.array([0, 1, 255])
    result[25:, 50:, :] = np.array([255, 255, 255])
    result[:25, 74:77, :] = np.array([1, 1, 1])
    result[24:27, :, :] = np.array([1, 1, 1])
    result[25:, 49:52, :] = np.array([1, 1, 1])
    return result


def generate_speckle(
    number_looks: int,
    sar_image: Optional[TSARImage] = None,
    shape: Optional[tuple[int, int, int, int] | tuple[int, int]] = None,
    random_state: Optional[np.random.RandomState] = None,
) -> TSARImage:
    """
    Simulate speckle according to Goodman's fully developed model.
    :param number_looks: the parameter of the Wishart distribution.
    :param sar_image: the underlying matrix field if any, identity otherwise.
    :param shape: the shape of the matrix field if `matrix_field` is not provided.
    :param random_state: the state of the random generator.
    :return: a field of Hermitian non-negative matrices. If `number_looks` is
        is larger that the matrix dimension, the field is positive definite.
    """
    if random_state is None:
        random_state = np.random.RandomState(746)

    if sar_image is None and shape is None:
        raise ValueError("Arguments `matrix_field` or `shape` must be given")
    if shape is None:
        assert sar_image is not None
        shape = sar_image.shape  # type: ignore

    assert shape is not None

    if sar_image is not None and sar_image.shape != shape:
        raise ValueError(
            f"Got incompatible dimensions ({sar_image.shape}) vs ({shape})"
        )

    if len(shape) == 4:
        is_scalar_image = False
    elif len(shape) == 2:
        is_scalar_image = True
        shape = (shape[0], shape[1], 1, 1)
        if sar_image is not None:
            sar_image = sar_image[:, :, np.newaxis, np.newaxis]  # type: ignore
    else:
        raise Exception(f"Unexpected shape {shape}")

    scatterers = (
        random_state.randn(*shape[:3], number_looks)
        + 1.0j * random_state.randn(*shape[:3], number_looks)
    ) / np.sqrt(2)

    noise_matrix_field = np.empty(shape, dtype=complex)
    for i in range(shape[3]):
        for j in range(i, shape[3]):
            noise_matrix_field[:, :, i, j] = np.mean(
                scatterers[:, :, i, :] * np.conj(scatterers[:, :, j, :]), axis=2
            )
            if j > i:
                noise_matrix_field[:, :, j, i] = np.conj(noise_matrix_field[:, :, i, j])

    if sar_image is None:
        noisy_matrix_field = noise_matrix_field
    else:
        stabalized_matrix_field = stabmatrices(sar_image)
        half_matrix_field = spfunpdmatrices(stabalized_matrix_field, np.sqrt)
        noisy_matrix_field = mulmatrices(
            mulmatrices(half_matrix_field, noise_matrix_field), half_matrix_field
        )

    if is_scalar_image:
        return noisy_matrix_field[:, :, 0, 0]  # type: ignore
    else:
        return noisy_matrix_field  # type: ignore


def simulate_polsar_from_rgb(
    rgb_image: RGBImage, inverse_condition_number: float = 1e-3
) -> MatrixField:
    """
    Synthesize a well conditioned and stabalized Hermitian positive definite
    field that ressemble the prescribed RGB image when rendered with fake
    colors based on its Pauli basis decomposition.
    :param rbg_image: the prescribed RGB image.
    :param inverse_condition_number: the desired minimum condition number.
    :return: the field of Hermitian positive definite matrices.
    """

    m, n, d = rgb_image.shape

    rgb_image = rgb_image.astype(np.float64)
    rgb_image = rgb_image - rgb_image.min() + 1
    if rgb_image.max() > rgb_image.min():
        rgb_image /= rgb_image.max() - rgb_image.min()

    result = np.zeros((m, n, d, d), dtype=complex)
    result[:, :, 0, 0] = (rgb_image[:, :, 2] + rgb_image[:, :, 0]) ** 2 / 4.0
    result[:, :, 1, 1] = rgb_image[:, :, 1] ** 2 / np.sqrt(2)
    result[:, :, 2, 2] = (rgb_image[:, :, 2] - rgb_image[:, :, 0]) ** 2 / 4.0
    result[:, :, 0, 2] = (
        (rgb_image[:, :, 2] ** 2 - rgb_image[:, :, 0] ** 2) * (1.0 + 0.0j) / 4.0
    )
    result[:, :, 0, 1] = 0.0
    result[:, :, 1, 2] = 0.0
    result[:, :, 1, 0] = 0.0
    result[:, :, 2, 0] = np.conj(result[:, :, 0, 2])
    result[:, :, 2, 1] = 0.0
    result = stabmatrices(result)
    result = condloading(
        image=result, inverse_condition_number=inverse_condition_number
    )
    return result
