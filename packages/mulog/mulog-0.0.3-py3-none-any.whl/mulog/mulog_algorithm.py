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
from typing import Iterator, Optional, TypeAlias, TypeVar, Union

from attrs import define
import numpy as np
import scipy.special as sc

from .condloading import condloading
from .diagloading import diagloading
from .gaussian_denoisers import GaussianDenoiser
from .hermitian_matrix_field import (
    LogChannelPCA,
    MatrixField,
    covariance_matrix_field_to_log_channels,
    log_channels_to_covariance_matrix_field,
)
from .pnp_admm import iter_pnp_admm
from .prox import prox_wishart_fisher_tippet
from .stabmatrices import stabmatrices
from .tools import ScalarImage, ScalarImageStack

SARImage: TypeAlias = Union[ScalarImage, MatrixField]

TSARImage = TypeVar("TSARImage", bound=SARImage)


@define
class MulogPresets:
    """
    A data object used to cache pre-processed information:
    - well conditioned and stabalized matrix field of noisy data.
    - channel decomposition used to initialize ADMM and Newton iterations.
    - the log-channel PCA transformation.
    """

    noisy_matrix_field: MatrixField
    initial_noisy_channels: ScalarImageStack
    pca: LogChannelPCA


def preset_mulog(
    sar_image: Union[ScalarImage, MatrixField],
    number_looks: float,
    prescribed_inverse_conditioning: float = 1e-4,
) -> MulogPresets:
    """
    Generate the presets from noisy observations and settings
    :param sar_image: a field of Wishart matrices (Hermitian and
        non-negative definite).
    :param number_looks: the shape parameter of the Wishart distribution.
    :param prescribed_inverse_conditioning: the minimum inverse condtion number
        used to condition the matrices.
    :return: an objects of presets to be used internally by MuLoG algorithm.
    """
    sar_image = sar_image.reshape(sar_image.shape, order="F")

    # Remove negative, zero entries, equal eigenvalues... (safegard)
    sar_image = stabmatrices(sar_image)

    # Diagonal loading
    sar_image = condloading(
        sar_image, inverse_condition_number=prescribed_inverse_conditioning
    )

    # Initialisation is biased in intensity and better conditioning
    #   - only the initialisation (helps to converge faster)
    #   - the original C will be given for the data fidelity term
    #   - get a more accurate matrix logarithm
    initial_noisy_matrix_field = sar_image * number_looks / np.exp(sc.psi(number_looks))
    initial_noisy_matrix_field = diagloading(
        initial_noisy_matrix_field, number_looks=number_looks
    )

    # Log-channel decomposition: y = OmegaInv(log C)
    initial_noisy_channels, pca = covariance_matrix_field_to_log_channels(
        initial_noisy_matrix_field, number_looks
    )

    return MulogPresets(
        noisy_matrix_field=sar_image,
        initial_noisy_channels=initial_noisy_channels,
        pca=pca,
    )


def iter_mulog(
    mulog_presets: MulogPresets,
    number_looks: float,
    denoiser: GaussianDenoiser,
    beta: Optional[float] = None,
    newton_iterations: int = 10,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> Iterator[ScalarImageStack]:
    """
    Iterate through the MuLoG sequence.
    :param mulog_presets: encapsulation of pre-processed observations.
    :param number_looks: the shape of the Wishart distribution.
    :param denoiser: a Gaussian denoiser.
    :param beta: internal parameter of ADMM. If None, set accordng to [1].
    :param newton_iterations: number of Newton iterations.
    :param eta: an internal parameter of Plug-n-Play ADMM.
    :param gamma: an internal parameter of Plug-n-Play ADMM.
    :return: an iterator over the sequence of converging solutions.
    """
    beta = 1 + 2 / number_looks if beta is None else beta

    yield from iter_pnp_admm(
        initialization=mulog_presets.initial_noisy_channels,
        proxllk=lambda x, lbd: prox_wishart_fisher_tippet(
            z=x,
            y=mulog_presets.noisy_matrix_field,
            lbd=lbd,
            initialization=mulog_presets.initial_noisy_channels,
            pca=mulog_presets.pca,
            number_looks=number_looks,
            newton_iterations=newton_iterations,
        ),
        denoiser=denoiser,
        sigma=1,
        beta=beta,
        gamma=gamma,
        eta=eta,
    )


def run_mulog_from_presets(
    mulog_presets: MulogPresets,
    number_looks: float,
    denoiser: GaussianDenoiser,
    beta: Optional[float] = None,
    admm_iterations: int = 6,
    newton_iterations: int = 10,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> MatrixField:
    """
    Run MuLoG from presets.
    :param mulog_presets: encapsulation of pre-processed observations.
    :param number_looks: the shape of the Wishart distribution.
    :param denoiser: a Gaussian denoiser.
    :param beta: internal parameter of ADMM. If None, set accordng to [1].
    :param admm_iterations: number of ADMM iterations.
    :param newton_iterations: number of Newton iterations.
    :param eta: an internal parameter of Plug-n-Play ADMM.
    :param gamma: an internal parameter of Plug-n-Play ADMM.
    :return: the MuLoG solution.
    """
    mulog_sequence = iter_mulog(
        mulog_presets=mulog_presets,
        number_looks=number_looks,
        denoiser=denoiser,
        beta=beta,
        newton_iterations=newton_iterations,
        gamma=gamma,
        eta=eta,
    )

    ## Run plug-and-play ADMM
    x = None
    for k in range(admm_iterations):
        x = next(mulog_sequence)

    assert x is not None

    # Return to the initial representation: Sigma = exp(Omega(x))
    denoised_image = log_channels_to_covariance_matrix_field(x, mulog_presets.pca)

    return denoised_image


def run_mulog(
    sar_image: TSARImage,
    number_looks: float,
    denoiser: GaussianDenoiser,
    beta: Optional[float] = None,
    admm_iterations: int = 6,
    newton_iterations: int = 10,
    prescribed_inverse_conditioning: float = 1e-4,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> TSARImage:
    """
    Run MuLoG from presets.
    :param sar_image: an image of SAR intensity or a field of Wishart matrices
        (Hermitian and non-negative definite) encoding PolSAR, InSAR, DualPolSAR,
        or PolInSAR data.
    :param number_looks: the shape of the Wishart distribution.
    :param denoiser: a Gaussian denoiser.
    :param beta: internal parameter of ADMM. If None, set accordng to [1].
    :param admm_iterations: number of ADMM iterations.
    :param newton_iterations: number of Newton iterations.
    :param prescribed_inverse_conditioning: the minimum inverse condtion number
        used to condition the matrices.
    :param eta: an internal parameter of Plug-n-Play ADMM.
    :param gamma: an internal parameter of Plug-n-Play ADMM.
    :return: the MuLoG solution.
    """
    # Input data format conversion
    if sar_image.ndim == 2:
        reshaped = True
        sar_image = sar_image[:, :, np.newaxis, np.newaxis]  # type: ignore
    elif sar_image.ndim == 4:
        reshaped = False
    else:
        raise Exception(
            "Argument `noisy_matrix_field` must be either a scala image "
            "or a field of matrices."
        )

    mulog_presets = preset_mulog(
        sar_image=sar_image,
        number_looks=number_looks,
        prescribed_inverse_conditioning=prescribed_inverse_conditioning,
    )

    denoised_image = run_mulog_from_presets(
        mulog_presets=mulog_presets,
        number_looks=number_looks,
        denoiser=denoiser,
        beta=beta,
        newton_iterations=newton_iterations,
        admm_iterations=admm_iterations,
        gamma=gamma,
        eta=eta,
    )

    # Output data format conversion
    if reshaped:
        denoised_image = denoised_image[:, :, 0, 0]

    return denoised_image  # type: ignore
