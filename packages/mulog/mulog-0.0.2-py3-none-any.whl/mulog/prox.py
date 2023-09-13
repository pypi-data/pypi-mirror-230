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
from typing import Callable, TypeVar

import numpy as np

from .hermitian_matrix_field import (
    LogChannelPCA,
    MatrixField,
    expmatrices_directional_derivative_from_internals_with_internals,
    expmatrices_internals,
    expmatrices_second_directional_derivative_internals_from_internals,
)
from .tools import (
    ScalarImageStack,
    ScalarSignal,
    compute_fisher_tippet_noise_std,
)

TScalarSignal = TypeVar("TScalarSignal", bound=ScalarSignal | float)


def proj_polynomial(z: ScalarSignal, deg: int) -> ScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + indicator(x is a polygon)

    where indicator(True) = 0 and indicator(False) = inf

    :param z: signal to project.
    :param deg: degrees of the polynom.
    :return: the projection of z.
    """
    omega = np.linspace(-1, 1, z.shape[0])
    hat = np.array([omega**k for k in range(deg + 1)])
    return hat.T @ np.linalg.lstsq(hat.T, z, rcond=None)[0]


def prox_l2(z: TScalarSignal, lbd: float) -> TScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + lbd ||x||**2 / 2

    :param z: signal to proximate.
    :param deg: proximal regularization parameter.
    :return: the solution.
    """
    return z / (1 + lbd)  # type: ignore


def prox_l1(z: TScalarSignal, lbd: float) -> TScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + lbd ||x||_1

    :param z: signal to proximate.
    :param lbd: proximal regularization parameter.
    :return: the solution.
    """
    if isinstance(z, np.ndarray):
        return np.where(np.abs(z) < lbd, 0.0, z - lbd * np.sign(z))  # type: ignore
    elif isinstance(z, float):
        return 0.0 if np.abs(z) < lbd else z - lbd * np.sign(z)  # type: ignore
    else:
        raise Exception("Unexpected type")


def prox_gaussian(
    z: TScalarSignal, y: TScalarSignal, lbd: float, sigma: float
) -> TScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + lbd ||x - y||**2 / (2 sigma**2)

    :param z: signal to proximate.
    :param y: the location parameter of the Gaussian distribution.
    :param lbd: proximal regularization parameter.
    :param sigma: the scale parameter of the Gaussian distribution.
    :return: the solution.
    """
    return y + sigma * prox_l2((z - y) / sigma, lbd / sigma**2)  # type: ignore


def prox_laplacian(
    z: TScalarSignal, y: TScalarSignal, lbd: float, sigma: float
) -> TScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + lbd * sqrt(2) * ||x - y|| / sigma

    :param z: signal to proximate.
    :param y: the location parameter of the Laplacian distribution.
    :param lbd: proximal regularization parameter.
    :param sigma: the scale parameter of the Laplacian distribution.
    :return: the solution.
    """
    gamma = sigma / np.sqrt(2)
    return y + gamma * prox_l1((z - y) / gamma, lbd / gamma**2)


def prox_projector(
    z: TScalarSignal,
    lbd: float,
    projector: Callable[[TScalarSignal], TScalarSignal],
) -> TScalarSignal:
    """
    Solve:

        argmin_x ||x - z||**2 / 2 + lbd ||x - Proj(x)||**2 / 2

    :param z: signal to proximate.
    :param lbd: proximal regularization parameter.
    :param projector: an orthogonal projector on a convex set.
    :return: the solution.
    """
    return (z + lbd * projector(z)) / (1 + lbd)  # type: ignore


def prox_fisher_tippet(
    z: TScalarSignal,
    y: TScalarSignal,
    lbd: float,
    number_looks: float,
    newton_iterations: int = 10,
) -> TScalarSignal:
    """
    Implement Newton iterations to solve:

        argmin_x ||x - z||**2 / 2 - lbd log p(y | x, number_looks)

    for x -> p(y | x) is the Fisher Tippet likelihood function

    :param z: signal to proximate.
    :param y: observations for the Fisher Tippet distribution.
    :param lbd: proximal regularization parameter.
    :param number_looks: the shape parameter of the Fisher Tippet distribution.
    :param newton_iterations: number of Newton iterations.
    :return: the solution.
    """
    x = prox_gaussian(
        z=z, y=y, lbd=lbd, sigma=compute_fisher_tippet_noise_std(number_looks)
    )
    for k in range(newton_iterations):
        gradient = x - z + lbd * number_looks * (1 - np.exp(y - x))
        gamma = 1 + lbd * number_looks * np.exp(y - x)
        x = x - gradient / gamma / 2

    return x  # type: ignore


def prox_wishart_fisher_tippet(
    z: ScalarImageStack,
    y: MatrixField,
    initialization: ScalarImageStack,
    pca: LogChannelPCA,
    lbd: float,
    number_looks: float,
    newton_iterations: int = 10,
) -> ScalarImageStack:
    """
    Implement Newton iterations to solve:

        argmin_x ||x - z||**2 / 2 - lbd log p(y | x, number_looks)

    for x -> p(y | x) is the Wishart Fisher Tippet likelihood function

    :param z: channel decomposition of the signal to proximate.
    :param y: observations for the Fisher Tippet distribution (a field of
        well conditioned, stabalized, positive definite Hermitian matrices)
    :param initialization: channel decomposition used to initialize Newton iterations.
    :param pca: the log-channel PCA transformation.
    :param lbd: the proximal regularization parameter.
    :param number_looks: the shape parameter of the Wishart Fisher Tippet distribution.
    :param newton_iterations: number of Newton iterations.
    :return: the solution.
    """

    m, n, d, d = y.shape

    identity_field = np.eye(d)[np.newaxis, np.newaxis]

    x = prox_gaussian(z=z, y=initialization, lbd=lbd, sigma=1.0)

    for k in range(newton_iterations):
        # compute gradient
        omega_x = pca.omega(x)

        exp_minus_omega_x_internals = expmatrices_internals(-omega_x)

        (
            exp_minus_omega_x_dd,
            exp_minus_omega_x_internals,
        ) = expmatrices_directional_derivative_from_internals_with_internals(
            precomputed_internals=exp_minus_omega_x_internals,
            direction=y,
        )

        gradient = (
            x
            - z
            + lbd * number_looks * pca.theta(identity_field - exp_minus_omega_x_dd)
        )

        # compute gradient direction
        gradient_norm = np.sqrt(np.sum(gradient**2, axis=0))
        zero_mask = gradient_norm == 0
        gradient_norm[zero_mask] = 1
        gradient_direction = gradient / gradient_norm[np.newaxis]
        gradient_direction[:, zero_mask] = 0.0

        # compute second derivative in d
        theta_adjoint_d = pca.theta_adjoint(gradient_direction)

        exp_minus_omega_x_internals = (
            expmatrices_second_directional_derivative_internals_from_internals(
                precomputed_internals=exp_minus_omega_x_internals,
                direction_b=theta_adjoint_d,
            )
        )

        # deduce gamma (the inverse of the second derivative in the direcrion d)
        dopt = np.real(
            np.sum(
                np.sum(
                    exp_minus_omega_x_internals.eigen_direction_b
                    * np.conj(exp_minus_omega_x_internals.matrix_f),
                    axis=2,
                ),
                axis=2,
            )
        )
        gamma = 1 + lbd * number_looks * np.abs(dopt)

        # Quasi newton update
        x = x - gradient / gamma[np.newaxis] / 2

    return x
