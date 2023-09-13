# pyprocessors_rf_resegment

[![license](https://img.shields.io/github/license/oterrier/pyprocessors_rf_resegment)](https://github.com/oterrier/pyprocessors_rf_resegment/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyprocessors_rf_resegment/workflows/tests/badge.svg)](https://github.com/oterrier/pyprocessors_rf_resegment/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyprocessors_rf_resegment)](https://codecov.io/gh/oterrier/pyprocessors_rf_resegment)
[![docs](https://img.shields.io/readthedocs/pyprocessors_rf_resegment)](https://pyprocessors_rf_resegment.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyprocessors_rf_resegment)](https://pypi.org/project/pyprocessors_rf_resegment/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyprocessors_rf_resegment)](https://pypi.org/project/pyprocessors_rf_resegment/)

Create segments from annotations

## Installation

You can simply `pip install pyprocessors_rf_resegment`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyprocessors_rf_resegment
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
