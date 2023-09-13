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
from typing import Callable, Iterator

import numpy as np

from .tools import ScalarSignal


def iter_pnp_admm(
    initialization: ScalarSignal,
    denoiser: Callable[[ScalarSignal, float], ScalarSignal],
    proxllk: Callable[[ScalarSignal, float], ScalarSignal],
    beta: float = 1.0,
    sigma: float = 1.0,
    lbd: float = 1.0,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> Iterator[ScalarSignal]:
    """
    Iterate thru Plug-and-Play ADMM to solve for some y (no need to provide y)

       x \\in \\argmin - \\log p(y | x) + \\lambda R(x)

    :param initialization: initialization for x (eg, y or the MLE of x for y).
    :param denoiser: function solving for some z and lambda

                     x = \\argmin 1/2 ||z - x||^2 + \\lambda R(x)

    :param proxllk: prox of x -> -\\log p(y | x) solving for some z and lambda

                     x = \\argmin 1/2 ||z - x||^2 - \\lambda \\log p(y | x)

    :param beta: internal parameter of ADMM.
    :param sigma: noise in y should be homoscedastic with variance sig^2.
    :param lambda: regularization parameter.
    :param eta: internal parameter of Plug-n-Play ADMM.
    :param gamma: internal parameter of Plug-n-Play ADMM.
    :return: an iterator of the iterates of the ADMM sequence.
    """

    x = initialization

    beta = beta * lbd / sigma**2

    z = denoiser(x, sigma)

    e = z - x
    x = z + e
    xold = x
    zold = z
    eold = e
    dold = np.inf

    while True:
        # Prox of log-likelihood
        x = proxllk(z + e, 1 / beta)

        yield x

        # Denoiser
        z = denoiser(x - e, np.sqrt(lbd / beta))

        # Residual update
        e = e + z - x

        # Block to guarantee convergence according to [3]
        d = (
            np.linalg.norm(xold - x)
            + np.linalg.norm(zold - z)
            + np.linalg.norm(eold - e)
        )
        if d > eta * dold:
            beta = gamma * beta
        xold = x
        zold = z
        eold = e
        dold = d


def run_pnp_admm(
    initialization: ScalarSignal,
    denoiser: Callable[[ScalarSignal, float], ScalarSignal],
    proxllk: Callable[[ScalarSignal, float], ScalarSignal],
    number_iterations: int = 6,
    beta: float = 1,
    sigma: float = 1,
    lbd: float = 1,
    eta: float = 0.95,
    gamma: float = 1.05,
) -> ScalarSignal:
    """
    Use Plug-and-Play ADMM to solve for some y (no need to provide y)

        x \\in \\argmin - \\log p(y | x) + \\lambda R(x)

    :param initialization: initialization for x (eg, y or the MLE of x for y).
    :param denoiser: function solving for some z and lambda

        x = \\argmin 1/2 ||z - x||^2 + \\lambda R(x)

    :param proxllk: prox of x -> -log p(y | x) solving for some z and lambda

        x = \\argmin 1/2 ||z - x||^2 - \\lambda log p(y | x)

    :param number_iterations: number `n` of ADMM iterations.
    :param beta: inner parameter of ADMM.
    :param sigma: noise in y should be homoscedastic with variance sig^2.
    :param lambda: regularization parameter.
    :param eta: a pParameter that guarantee convergence.
    :param gamma: a parameter that guarantee convergence.
    :return: `n`-th iterate of the ADMM sequence.
    """

    pnp_admm_sequence = iter_pnp_admm(
        initialization=initialization,
        denoiser=denoiser,
        proxllk=proxllk,
        beta=beta,
        sigma=sigma,
        lbd=lbd,
        eta=eta,
        gamma=gamma,
    )

    x = initialization
    for k in range(number_iterations):
        x = next(pnp_admm_sequence)

    return x
