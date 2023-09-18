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

from typing import Iterator, Optional

import numpy as np

from .gaussian_denoisers import GaussianDenoiser
from .pnp_admm import iter_pnp_admm
from .prox import prox_fisher_tippet
from .tools import (
    ScalarSignal,
    compute_fisher_tippet_noise_bias,
    compute_fisher_tippet_noise_std,
)


def iter_log_midal(
    sar_signal: ScalarSignal,
    number_looks: float,
    denoiser: GaussianDenoiser,
    beta: Optional[float] = None,
    newton_iterations: int = 10,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> Iterator[ScalarSignal]:
    """
    Iterate through the MIDAL sequence, see:

        Bioucas-Dias, José M., and Mário AT Figueiredo. "Multiplicative noise removal
        using variable splitting and constrained optimization." IEEE Transactions on
        Image Processing 19.7 (2010): 1720-1730.

    :param sar_signal: a signal or image of Fisher-Tippet observations.
    :param number_looks: the shape of the Fisher-Tippet distribution.
    :param denoiser: a Gaussian denoiser.
    :param beta: internal parameter of ADMM. If None, set accordng to [1].
    :param newton_iterations: number of Newton iterations.
    :param eta: an internal parameter of Plug-n-Play ADMM.
    :param gamma: an internal parameter of Plug-n-Play ADMM.
    :return: an iterator over the sequence of converging solutions.
    """

    beta = 1 + 2 / number_looks if beta is None else beta

    sigma = compute_fisher_tippet_noise_std(number_looks)

    yield from iter_pnp_admm(
        initialization=sar_signal - compute_fisher_tippet_noise_bias(number_looks),
        proxllk=lambda x, lbd: prox_fisher_tippet(
            z=x,
            y=sar_signal,
            lbd=lbd,
            number_looks=number_looks,
            newton_iterations=newton_iterations,
        ),
        denoiser=denoiser,
        sigma=sigma,
        beta=beta,
        eta=eta,
        gamma=gamma,
    )


def run_midal(
    sar_signal: ScalarSignal,
    number_looks: float,
    denoiser: GaussianDenoiser,
    beta: Optional[float] = None,
    admm_iterations: int = 6,
    newton_iterations: int = 10,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> ScalarSignal:
    """
    Run MIDAL Algorithm, see:

        Bioucas-Dias, José M., and Mário AT Figueiredo. "Multiplicative noise removal
        using variable splitting and constrained optimization." IEEE Transactions on
        Image Processing 19.7 (2010): 1720-1730.

    :param sar_signal: a signal or image of positive Gamma observations.
    :param number_looks: the shape of the Fisher-Tippet distribution.
    :param denoiser: a Gaussian denoiser.
    :param beta: internal parameter of ADMM. If None, set accordng to [1].
    :param newton_iterations: number of Newton iterations.
    :param eta: an internal parameter of Plug-n-Play ADMM.
    :param gamma: an internal parameter of Plug-n-Play ADMM.
    :return: the solution.
    """
    log_midal_sequence = iter_log_midal(
        sar_signal=np.log(sar_signal),
        number_looks=number_looks,
        denoiser=denoiser,
        beta=beta,
        newton_iterations=newton_iterations,
        eta=eta,
        gamma=gamma,
    )

    log_midal_solution = None
    for k in range(admm_iterations):
        log_midal_solution = next(log_midal_sequence)

    assert log_midal_solution is not None

    return np.exp(log_midal_solution)
