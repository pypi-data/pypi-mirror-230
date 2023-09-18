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

from .channel_decomposition import (
    MatrixField as MatrixField,
    getchannels as getchannels,
    getmatrices as getmatrices,
    getmatrices_adj as getmatrices_adj,
)
from .linear_algebra import (
    adjmatrices as adjmatrices,
    eigmatrices as eigmatrices,
    logmatrices as logmatrices,
    mulmatrices as mulmatrices,
    spfunmatrices as spfunmatrices,
    spfunpdmatrices as spfunpdmatrices,
    spfunscalars as spfunscalars,
    tracematrices as tracematrices,
)
from .log_channel_decomposition import (
    LogChannelPCA as LogChannelPCA,
    covariance_matrix_field_to_log_channels as covariance_matrix_field_to_log_channels,
    log_channels_to_covariance_matrix_field as log_channels_to_covariance_matrix_field,
)
from .matrix_exponentials import (
    expmatrices as expmatrices,
    expmatrices_directional_derivative as expmatrices_directional_derivative,
    expmatrices_directional_derivative_from_internals as expmatrices_directional_derivative_from_internals,  # noqa: E501
    expmatrices_directional_derivative_from_internals_with_internals as expmatrices_directional_derivative_from_internals_with_internals,  # noqa: E501
    expmatrices_directional_derivative_with_internals as expmatrices_directional_derivative_with_internals,  # noqa: E501
    expmatrices_internals as expmatrices_internals,
    expmatrices_second_directional_derivative as expmatrices_second_directional_derivative,  # noqa: E501
    expmatrices_second_directional_derivative_internals_from_internals as expmatrices_second_directional_derivative_internals_from_internals,  # noqa: E501
    expmatrices_with_internals as expmatrices_with_internals,
)
