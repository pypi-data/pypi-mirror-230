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

from .condloading import condloading as condloading
from .diagloading import diagloading as diagloading
from .gaussian_denoisers import (
    GaussianDenoiser as GaussianDenoiser,
    run_autoscaled_bm3d as run_autoscaled_bm3d,
    run_tv_denoising as run_tv_denoising,
)
from .midal_algorithm import (
    iter_log_midal as iter_log_midal,
    run_midal as run_midal,
)
from .mulog_algorithm import (
    iter_mulog as iter_mulog,
    preset_mulog as preset_mulog,
    run_mulog as run_mulog,
    run_mulog_from_presets as run_mulog_from_presets,
)
from .pnp_admm import (
    iter_pnp_admm as iter_pnp_admm,
    run_pnp_admm as run_pnp_admm,
)
from .prox import (
    TScalarSignal as TScalarSignal,
    proj_polynomial as proj_polynomial,
    prox_fisher_tippet as prox_fisher_tippet,
    prox_gaussian as prox_gaussian,
    prox_l1 as prox_l1,
    prox_l2 as prox_l2,
    prox_laplacian as prox_laplacian,
    prox_projector as prox_projector,
    prox_wishart_fisher_tippet as prox_wishart_fisher_tippet,
)
from .sar_image_generation import (
    generate_mondrian_image as generate_mondrian_image,
    generate_speckle as generate_speckle,
    simulate_polsar_from_rgb as simulate_polsar_from_rgb,
)
from .sar_image_rendering import (
    RGBImageRenderer as RGBImageRenderer,
    SARImageRenderer as SARImageRenderer,
)
from .stabmatrices import stabmatrices as stabmatrices
from .tools import (
    RGBImage as RGBImage,
    ScalarImage as ScalarImage,
    ScalarImageStack as ScalarImageStack,
    ScalarSignal as ScalarSignal,
    compute_fisher_tippet_noise_bias as compute_fisher_tippet_noise_bias,
    compute_fisher_tippet_noise_std as compute_fisher_tippet_noise_std,
    estimate_gaussian_noise_std_with_mad as estimate_gaussian_noise_std_with_mad,
    estimate_gaussian_noise_std_with_mad_per_channel as estimate_gaussian_noise_std_with_mad_per_channel,  # noqa: E501
    fftgrid as fftgrid,
)
