This is a Python 3.10 implementation of MuLoG as described in reference [2].

MuLoG is a plug-and-play ADMM approach for (Pol/In)SAR image speckle
reduction using an off-the-shelf Gaussian denoiser and matrix
logarithm transform to stabilized noise and simplify the optimization.

# Description

Synthetic aperture radar (SAR) images are widely used for Earth
observation to complement optical imaging. By combining information on
the polarization and the phase shift of the radar echos, SAR images
offer high sensitivity to the geometry and materials that compose a
scene. This information richness comes with a drawback inherent to all
coherent imaging modalities: a strong signal-dependent noise called
"speckle". MuLoG algorithm addresses the mathematical issues of performing
speckle reduction in a transformed domain: the matrix-log
domain. Rather than directly estimating noiseless covariance matrices,
recasting the denoising problem in terms of the matrix-log of the
covariance matrices stabilizes noise fluctuations and makes it
possible to apply off-the-shelf denoising algorithms.

While a large diversity of speckle reduction methods exist for
intensity images, only few can be extended to process multi-channel
SAR images. In particular, extension of variational methods lead to
challenging optimization problems due to the non-convexity of the
neg-log-likelihood and the positive definiteness constraint on the
covariance matrices. Furthermore, signal and channel dependent
variance lead to restoration results with an uneven suppression of
speckle. This algorithm introduced a general scheme based on a matrix
logarithm transform to approximately stabilize speckle variance and
produce close to independent channels. Each channel can then be
processed with the user-defined Gaussian denoiser. Upon re-iterating, a
good fit of the restored multi-channel image with the Wishart
distribution of input covariance matrices is enforced.

# Installation

Unless you have Python 3.10 installed and enabled as default, we recommend
installing MuLoG in a virtual environment as described in the following section.

## Set up a virtual environment (optional)

We recommend installing MuLoG in a virtual environment such as `venv`. You can
install `venv` for Python 3.10 on Debian/Ubuntu as follows:

	sudo apt install python3.10-venv

If your system does not have Python 3.10, please refer to the "Troubleshooting"
section below.

Create and activate your virtual environment by running the following either directly
in the directory in which you will execute or clone MuLoG or in a parent directory, as

	python3 -m venv venv
	source venv/bin/activate

Alternatively, you can use other environment systems such as `conda`.

## Latest stable version

We recommend installing the latest stable version of MuLoG by running

	pip3 install mulog

in a system or environment with Python 3.10.

## Development version

Alternatively, you can install the development version from `git` as

	pip3 install -e git+https://bitbucket.org/charles_deledalle/mulog2022-python.git#egg=mulog

or, directly from the sources as

	git clone https://bitbucket.org/charles_deledalle/mulog2022-python.git
	cd mulog2022-python
	python3 setup.py sdist
	python3 setup.py install

# Run MuLoG

Examples on how to run mulog are provided in two scripts that you can execute as:
```shell
# Run MuLoG on a multlooked synthetic PolSAR image with 5 looks
python3 -m mulog.mulog_synthetic_example -l 5

# Run MuLoG on PolSAR images from a small PolSAR image
python3 -m mulog.mulog_examples -e sanfrancisco
```

If the execution stops with the warning "UserWarning: Matplotlib is currently using agg [...]",
please refer to the "Troubleshooting" section below.

For more details on how to execute these examples, see:

	python3 -m mulog.mulog_synthetic_example --help
	python3 -m mulog.mulog_examples --help

To run MuLoG on your own data, you need to execute from Python the function
called `run_mulog` that you can import as:

	from mulog.mulog_algorithm import run_mulog

This function takes your data as input through the argument `noisy_matrix_field`
which has the format of a covariance matrix field (an image of non negative
definite complex Hermitian matrices). It's your responsibility to load and
format your data in Python to make it compatible with this input. SAR, InSAR,
PolSAR, DualPolSAR PolInSAR images can be formatted as such a matrix field. For
more details, please read [1-2].

# List of the files in this folder

- ```condloading.py```

The code in this file, corresponding to Algorithm 5 of the paper, rescales the
range of the eigenvalues of each matrix of a bi-dimensional field into a
potentially smaller range to make sure that their condition number doesn't
exceed the chosen threshold. It is applied on MuLoG input to compute the
bi-dimensional field that will be used in the definition of the proximal operator
of the data fidelity.

- ```diagloading.py```

This file contains an implementation of Algorithm 4 of the paper which describes
the process of correcting the coherence of MuLoG input in order to lessen the
bias that will be introduced in the following steps. The result will serve as a
starting point for the PnP-ADMM and helps to speed up the convergence.

- ```gaussian_denoisers.py```

Contains the function used in ADMM iterations to apply independently bm3d (a
Gaussian denoiser) or TV on each channel of its input. The computational speed
can be improved by parallelizing the process (which is not done here).

- ```hermitian_matrix_field/channel_decomposition.py```
- ```hermitian_matrix_field/linear_algebra.py```
- ```hermitian_matrix_field/log_channel_decomposition.py```
- ```hermitian_matrix_field/matrix_exponentials.py```

These files group the functions for the different transforms (and their inverse)
to be performed on bi-dimensional fields of matrices including the multiplication
transform, the matrix exponential transform, and the transform that decomposes
3x3 complex covariance matrices into 9 real-valued.

- ```midal_algorithm.py```

Implementation of Midal (mono channel version of MuLoG). This is the algorithm
that MuLoG extend to multichannel SAR images.

- ```mulog_algorithm.py```

Implementation of MuLoG as described in [2].

- ```mulog_examples.py```

A cli tool to run MuLoG on a PolSAR example from a small dataset.

- ```mulog_synthetic_example.py```

A cli tool to run MuLoG on a synthetic example.

- ```pnp_admm.py```

Contains the code for PnP-ADMM iterations.

- ```prox.py```

Implementations of proximal operators used by MuLoG, Midal and for the sake of
unit tests.

- ```sar_image_generation.py```

Tools to generate synthetic mono-channel and multichannel SAR images.

- ```sar_image_rendering.py```

Tools to render mono-channel and multichannel SAR images with proper
adjustments (range clipping, gamma correction...).

- ```stabmatrices.py```

Add infinitesimal variations in any Hermitian matrix this such that the matrix does not
have true zeros, exact equal eigenvalues, or low rank. Recall that the space of such matrices
is dense in the space of Hermitian matrices.

- ```tools.py```

This file mostly contains various functions that MuLoG depends on.

# Developers

## Set up

Clone the git repository on your machine:

	git clone https://bitbucket.org/charles_deledalle/mulog2022-python.git
	cd mulog2022-python

Set up a Python 3.10 virtual environment as described in the Installation section above.
Once your virtual environment is set up and activated, install dependencies as

	pip3 install -r requirements.txt

## Contribution

Any contributions must be submitted through peer reviews.
Ask for an author account on the bitbucket repository,
create your own branch and raise a pull-request.
All additional code must be cover by a unit test.
Any pull request needs to pass the following commands before approval:

	black .
	ruff --fix .
	pyright .
	python3 -m pytest

Make sure to update `requirements.txt` to include any extra dependencies.

## Distribution

To distribute the project make sure to uptick the version number in `setup.py`
and merge that upticked version on the `master` branch.
Once the `master` branch is ready, run the following

	git checkout master
	cd $(git rev-parse --show-toplevel)
	rm -rf dist/ build/ mulog.egg-info/
	git status --porcelain

and make sure the last command did not print anything.
After that, generate the distribution files by running

	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*
	python3 -m twine upload -r testpypi dist/*

Test in a different environment

	mkdir /tmp/test
	cd /tmp/test
	python3 -m venv venv
	source venv/bin/activate
	pip3 install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mulog
	python3 -m mulog.mulog_synthetic_example -l 5

Finally, publish the final version

	python3 -m twine upload dist/*

Once done, tag the `master` branch with the new version number on Git.

# Troubleshooting

## How to fix "Unable to locate package python3.10-venv" on Debian/Ubuntu?

In case Python 3.10 is not available for your Debian/Ubuntu distribution,
we recommend you to install `pyenv` (https://github.com/pyenv/pyenv).
At the time this documentation has been written, you can install `pyenv` as follow:

	git clone https://github.com/pyenv/pyenv.git ~/.pyenv

Once `pyenv` is installed, you can install Python 3.10 inside `pyenv` as:

	sudo apt install python3-tk tk-dev libsqlite3-dev libbz2-dev libncurses-dev libreadline-dev
	CONFIGURE_OPTS="--enable-shared" ~/.pyenv/bin/pyenv install 3.10

After this, you can call Python 3.10 as

	~/.pyenv/versions/3.10.*/bin/python3

Note that we do not encourage you to add that path in your `PATH` environment.
Instead, as recommended above, use `venv` as follows

	~/.pyenv/versions/3.10.*/bin/python3 -m venv venv
	source venv/bin/activate

After your virtual environment is activated, you can proceed with the installation
of MuLoG either by following the "Latest stable version" or "Development version" instructions.

## How to fix "UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure"?

You need to activate a GUI default backend for Matplotlib compatible with your system.
For more information see https://matplotlib.org/stable/users/explain/backends.html).

If you are using Debian/Ubuntu, we recommend you using `tk` as backend,
that you can install as

	sudo apt install python3-tk

# License

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

# Contributors

- Charles Deledalle (original version in Matlab)
- Sébastien Mounier (translation in Python)
- Cristiano Ulondu Mendes (bug fixes and improvements from MuLoG2022)

# Scientific articles describing the method

Any published materials derived from MuLoG must cite [1-2].

[1] Deledalle, C. A., Denis, L., Tabti, S., & Tupin, F. (2017). MuLoG,
    or how to apply Gaussian denoisers to multi-channel SAR speckle
    reduction?. IEEE Transactions on Image Processing, 26(9), 4389-4403.

[2] Deledalle, C. A., Denis, L., & Tupin, F. (2022). Speckle reduction
    in matrix-log domain for synthetic aperture radar imaging. Journal
    of Mathematical Imaging and Vision, 64(3), 298-320.
