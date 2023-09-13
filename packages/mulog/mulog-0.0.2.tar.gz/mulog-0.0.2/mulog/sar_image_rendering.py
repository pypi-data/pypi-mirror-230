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

from typing import Generic, TypeVar, Union

from attr import define
import numpy as np
from strenum import StrEnum
from typing_extensions import Self

from .hermitian_matrix_field import MatrixField
from .mulog_algorithm import SARImage
from .tools import RGBImage, ScalarImage


class RenderImageAdjustments(StrEnum):
    NO = "no"  # keep the original range
    AUTO = "auto"  # range is determined form extreme values
    M1S = "m1s"  # range is [0 m+s] where m and s are the mean and std
    M2S = "m2s"  # range is [0 m+2*s]
    M3S = "m3s"  # range is [0 m+3*s]


TImage = TypeVar("TImage", bound=Union[ScalarImage, RGBImage])


@define
class RGBImageRenderer(Generic[TImage]):
    min_value: float
    max_value: float

    @classmethod
    def from_guide(
        cls,
        image_guide: TImage,
        value_range: tuple[float, float] = (0.0, 255.0),
        alpha: float = 1.0,
        beta: float = 1.0,
        adjust: RenderImageAdjustments = RenderImageAdjustments.NO,
    ) -> Self:
        """
        Instantiate a renderer to best capture the dynamic of a given image guide.
        :param image_guide: the image on which to adjust.
        :param value_range: range on which pixel values are mapped.
        :param alpha: gamma correction consisting of beta * img**alpha.
        :param beta: gamma correction consisting of beta * img**alpha.
        :param adjust: startegy by wich to redefine the range automatically.
        :return: the image renderer.
        """

        enhanced_guide = beta * image_guide**alpha

        if adjust == RenderImageAdjustments.NO:
            min_value, max_value = value_range
        elif adjust == RenderImageAdjustments.AUTO:
            min_value = np.min(enhanced_guide)
            max_value = np.max(enhanced_guide)
        elif adjust == RenderImageAdjustments.M3S:
            min_value = 0.0
            max_value = np.mean(enhanced_guide) + 3.0 * np.std(enhanced_guide)
        elif adjust == RenderImageAdjustments.M2S:
            min_value = 0.0
            max_value = np.mean(enhanced_guide) + 2.0 * np.std(enhanced_guide)
        elif adjust == RenderImageAdjustments.M1S:
            min_value = 0.0
            max_value = np.mean(enhanced_guide) + 1.0 * np.std(enhanced_guide)
        else:
            raise Exception(f"Render adjustment '{adjust}' unknown")

        if min_value >= max_value:
            min_value = -1.0
            max_value = 1.0

        return cls(
            min_value=float(min_value),
            max_value=float(max_value),
        )

    def render(
        self,
        image: TImage,
        normalize: bool = False,
    ) -> TImage:
        """
        Render an image for best display.
        :param image: the image to render.
        :param normalize: whether ot not to normalize the output.
        :return: the adjusted image.
        """

        image = image.clip(self.min_value, self.max_value)

        if normalize:
            return (image - self.min_value) / (
                self.max_value - self.min_value
            )  # type: ignore
        else:
            return image


def _sar_image_to_pauli(sar_image: SARImage) -> RGBImage:
    """
    Given a matrix field extract an RGB image from its Pauli decomposition
    :param sar_image: sar image
    :return: RGB image
    """

    if sar_image.ndim == 2:
        sar_image = sar_image[:, :, np.newaxis, np.newaxis]

    n1, n2, d, d = sar_image.shape

    if d == 1:
        return np.tile(sar_image[:, :, 0, 0].real[:, :, np.newaxis], [1, 1, 3])

    elif d == 2:
        pauli = np.zeros((n1, n2, 3), dtype=float)
        pauli[:, :, 2] = (
            sar_image[:, :, 0, 0] + sar_image[:, :, 1, 1] + 2 * sar_image[:, :, 0, 1]
        ).real
        pauli[:, :, 0] = (
            sar_image[:, :, 0, 0] + sar_image[:, :, 1, 1] - 2 * sar_image[:, :, 0, 1]
        ).real
        pauli[:, :, 1] = (sar_image[:, :, 0, 0] + sar_image[:, :, 1, 1]).real

    elif d == 3:
        pauli = np.zeros((n1, n2, 3), dtype=float)
        pauli[:, :, 2] = (
            sar_image[:, :, 0, 0] + sar_image[:, :, 2, 2] + 2 * sar_image[:, :, 0, 2]
        ).real
        pauli[:, :, 0] = (
            sar_image[:, :, 0, 0] + sar_image[:, :, 2, 2] - 2 * sar_image[:, :, 0, 2]
        ).real
        pauli[:, :, 1] = np.sqrt(2) * sar_image[:, :, 1, 1].real

    else:
        raise NotImplementedError(f"Not implemented for d={d}")

    return pauli


@define
class SARImageRenderer:
    rgb_scalings: tuple[float, float, float]
    image_renderer: RGBImageRenderer[RGBImage]

    @classmethod
    def from_guide(
        cls,
        sar_image_guide: SARImage,
    ) -> Self:
        """
        Instantiate a SAR renderer to best capture the dynamic of a given image guide.
        """
        d = 1 if sar_image_guide.ndim == 2 else sar_image_guide.shape[2]

        pauli = _sar_image_to_pauli(sar_image=sar_image_guide)

        rgb_scalings = np.quantile(np.real(np.abs(pauli)), 0.95, axis=(0, 1))

        if d == 3:
            rgb_scalings[[0, 2]] = np.max(rgb_scalings[[0, 2]])

        pauli = pauli / rgb_scalings

        return cls(
            rgb_scalings=rgb_scalings,
            image_renderer=RGBImageRenderer.from_guide(
                image_guide=np.sqrt(pauli),
                adjust=(
                    RenderImageAdjustments.M2S if d > 1 else RenderImageAdjustments.M3S
                ),
            ),
        )

    def render(self, sar_image: SARImage) -> RGBImage:
        """
        Render a SAR or PolSAR image into a
        :param sar_image: an image of gamma or Wishart distributed observations.
        :return: the image, its minimum value and maximum value.
        """
        pauli = _sar_image_to_pauli(sar_image=sar_image)
        pauli = pauli / self.rgb_scalings
        return self.image_renderer.render(image=np.sqrt(pauli), normalize=True)
