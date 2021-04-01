# Backlash Model with Linear Decision Boundaries (blm)

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/famura/blm/branch/master/graph/badge.svg?token=ESUTNFwtYY)](https://codecov.io/gh/famura/blm)
[![codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A simple model to describe the backlash effect into physics simulations based on numpy

The model implemented in this package was published as:  
J. Vörös, "Modeling and identification of systems with backlash", Automatica, 2008, [link to pdf](https://www.researchgate.net/profile/Jozef-Voeroes/publication/233692268_Identification_of_cascade_systems_with_backlash/links/56b3535f08ae3d06a266451d/Identification-of-cascade-systems-with-backlash.pdf)

## Citing

If you use code or ideas from this repository for your projects or research, please cite it.
```
@misc{Muratore_SimuRLacra,
  author = {Fabio Muratore},
  title = {blm - A simple model to describe the backlash effect into physics simulations},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/famura/blm}}
}
```

## Installation

To install the core part of the package run
```
pip install blm
```

For (local) development install the dependencies with
```
pip install -e .[dev]
```

## Getting Started

Play around with the model's parameters in the `demo.py` scirpt
```
cd examples
python demo.py
```

![demo](assets/demo.png?raw=true "output of demo.py")