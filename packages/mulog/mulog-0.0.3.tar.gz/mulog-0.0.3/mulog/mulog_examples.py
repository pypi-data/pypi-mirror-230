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
import argparse
import gzip
import os
import pickle

from attrs import define
import matplotlib.pyplot as plt
from strenum import StrEnum

from .gaussian_denoisers import (
    PREDEFINED_GAUSSIAN_DENOISER_NAMES_TO_DENOISER,
    PredefinedGaussianDenoiserNames,
)
from .mulog_algorithm import run_mulog
from .sar_image_rendering import SARImageRenderer


class MulogExampleNames(StrEnum):
    SANFRANCISCO = "sanfrancisco"
    SHANGHAI = "shanghai"
    LABRADOR = "labrador"
    TSUKABA = "tsukaba"


@define
class MulogExampleCase:
    path: str
    number_looks: float


MULOG_EXAMPLE_NAME_TO_CASE_MAPPING: dict[MulogExampleNames, MulogExampleCase] = {
    MulogExampleNames.SANFRANCISCO: MulogExampleCase(
        path="artifacts/sanfrancisco_airsar.pickle.gz",
        number_looks=2.7,
    ),
    MulogExampleNames.SHANGHAI: MulogExampleCase(
        path="artifacts/shanghai_sentinel1.pickle.gz",
        number_looks=1.2,
    ),
    MulogExampleNames.LABRADOR: MulogExampleCase(
        path="artifacts/labrador_sentinel1.pickle.gz",
        number_looks=1.2,
    ),
    MulogExampleNames.TSUKABA: MulogExampleCase(
        path="artifacts/tsukaba_pisar.pickle.gz",
        number_looks=2,
    ),
}


def run_mulog_example(
    case: MulogExampleCase,
    gaussian_denoiser_name: PredefinedGaussianDenoiserNames,
    block: bool = True,
):
    full_path = os.path.join(os.path.dirname(__file__), case.path)
    with gzip.open(full_path, "rb") as f:
        speckled_polsar_image = pickle.load(f)

    mulog_polsar_image = run_mulog(
        sar_image=speckled_polsar_image,
        number_looks=case.number_looks,
        denoiser=PREDEFINED_GAUSSIAN_DENOISER_NAMES_TO_DENOISER[gaussian_denoiser_name],
    )

    sar_image_render = SARImageRenderer.from_guide(
        sar_image_guide=speckled_polsar_image
    )

    _, axes = plt.subplots(ncols=2, figsize=(12, 6), sharex=True, sharey=True)
    axes[0].imshow(sar_image_render.render(speckled_polsar_image))
    axes[0].set_title("PolSAR image with speckle")
    axes[1].imshow(sar_image_render.render(mulog_polsar_image))
    axes[1].set_title("PolSAR image processed by MuLoG")
    plt.show(block=block)


if __name__ == "__main__":
    """
    Examples:

       python mulog_examples.py --help
       python mulog_examples.py -e sanfrancisco
       python mulog_examples.py --example_name tuskaba
       python mulog_examples.py -e sanfrancisco -g nlmeans

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--example_name",
        type=MulogExampleNames,
        default=MulogExampleNames.SANFRANCISCO,
        help=(
            f"Case name of the example, one of "
            f"{[name.value for name in MulogExampleNames]}"
        ),
    )
    parser.add_argument(
        "-g",
        "--gaussian_denoiser_name",
        type=PredefinedGaussianDenoiserNames,
        default=PredefinedGaussianDenoiserNames.BM3D,
        help=(
            f"Gaussian denoiser name, one of "
            f"{[name.value for name in PredefinedGaussianDenoiserNames]}"
        ),
    )
    args = parser.parse_args()

    run_mulog_example(
        case=MULOG_EXAMPLE_NAME_TO_CASE_MAPPING[args.example_name],
        gaussian_denoiser_name=args.gaussian_denoiser_name,
    )
