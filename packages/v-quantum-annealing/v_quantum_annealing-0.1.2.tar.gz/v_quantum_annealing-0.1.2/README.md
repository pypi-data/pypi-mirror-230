# v_quantum_annealing : Framework for the Ising model and QUBO.

[![PyPI version shields.io](https://img.shields.io/pypi/v/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![PyPI implementation](https://img.shields.io/pypi/implementation/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![PyPI format](https://img.shields.io/pypi/format/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![PyPI license](https://img.shields.io/pypi/l/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![PyPI download month](https://img.shields.io/pypi/dm/v_quantum_annealing.svg)](https://pypi.python.org/pypi/v_quantum_annealing/)
[![Downloads](https://pepy.tech/badge/v_quantum_annealing)](https://pepy.tech/project/v_quantum_annealing)

[![CPP Test](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/ci-test-cpp.yml/badge.svg)](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/ci-test-cpp.yml)
[![Python Test](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/ci-test-python.yaml/badge.svg)](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/ci-test-python.yaml)
[![Build Documentation](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/buid-doc.yml/badge.svg)](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/buid-doc.yml)
[![CodeQL](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/v_quantum_annealing/v_quantum_annealing/actions/workflows/codeql-analysis.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0204475dc07d48ffa851480d03db759e)](https://www.codacy.com/gh/v_quantum_annealing/v_quantum_annealing/dashboard?utm_source=github.com&utm_medium=referral&utm_content=v_quantum_annealing/v_quantum_annealing&utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/3b2f43f3e601ae74c497/maintainability)](https://codeclimate.com/github/v_quantum_annealing/v_quantum_annealing/maintainability)
[![codecov](https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing/branch/main/graph/badge.svg?token=WMSK3GS8E5)](https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing)

## Coverage Graph

| **Sunburst**                                                                                                                                                         | **Grid**                                                                                                                                                         | **Icicle**                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| <a href="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing"><img src="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing/branch/main/graphs/sunburst.svg?token=WMSK3GS8E5" width="100%"/></a> | <a href="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing"><img src="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing/branch/main/graphs/tree.svg?token=WMSK3GS8E5" width="100%"/></a> | <a href="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing"><img src="https://codecov.io/gh/v_quantum_annealing/v_quantum_annealing/branch/main/graphs/icicle.svg?token=WMSK3GS8E5" width="100%"/></a> |

- python >= 3.7
- (optional) gcc >= 7.0.0
- (optional) cmake >= 3.22
- (optional) Ninja

### Change **IMPORT**

- v_quantum_annealing >= v0.5.0

  ```python
  import v_quantum_annealing.cxxvqa
  ```

- v_quantum_annealing <= v0.4.9

  ```python
  import cxxvqa
  ```

- [Documents](https://v_quantum_annealing.github.io/v_quantum_annealing/)

- [C++ Docs](https://v_quantum_annealing.github.io/v_quantum_annealing-Reference-Page/index.html)

## install

### install via pip

> Note: To use GPGPU algorithms, please follow the section [`install via pip from source codes`](#install-via-pip-from-source-codes) below.
> GPGPU algorithms are automatically enabled once CMake finds CUDA frameworks during installation.

```
# Binary
$ pip install v_quantum_annealing 
# From Source (CUDA)
$ pip install --no-binary=v_quantum_annealing v_quantum_annealing
```

### install via pip from source codes

To install v_quantum_annealing from source codes, please install CMake first then install v_quantum_annealing.

#### cmake setup

If you want to use setup.py instead of PIP, You will need to install CMake>=3.22.\
We are Highly recommended install CMake via PYPI.

```
$ pip install -U cmake
```

Make sure the enviroment path for CMake is set correctly.

#### install v_quantum_annealing

```
$ pip install --no-binary=v_quantum_annealing v_quantum_annealing
```

### install from github repository

```
$ git clone git@github.com:v_quantum_annealing/v_quantum_annealing.git
$ cd v_quantum_annealing
$ python -m pip install -vvv .
```

## For Contributor

Use `pre-commit` for auto chech before git commit.
`.pre-commit-config.yaml`

```
# pipx install pre-commit 
# or 
# pip install pre-commit
pre-commit install
```

## Test

### Python

```sh
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install pip-tools 
$ pip-compile setup.cfg
$ pip-compile dev-requirements.in
$ pip-sync requirements.txt dev-requirements.txt
$ source .venv/bin/activate
$ export CMAKE_BUILD_TYPE=Debug
$ python setup.py --force-cmake install --build-type Debug -G Ninja
$ python setup.py --build-type Debug test 
$ python -m coverage html
```

### C++

```sh
$ mkdir build 
$ cmake -DCMAKE_BUILD_TYPE=Debug -S . -B build
$ cmake --build build --parallel
$ cd build
$ ./tests/cxxvqa_test
# Alternatively  Use CTest 
$ ctest --extra-verbose --parallel --schedule-random
```

Needs: CMake > 3.22, C++17

- Format

```sh
$ pip-compile format-requirements.in
$ pip-sync format-requirements.txt
```

```sh
$ python -m isort 
$ python -m black 
```

- Aggressive Format

```sh
$ python -m isort --force-single-line-imports --verbose ./v_quantum_annealing
$ python -m autoflake --in-place --recursive --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables ./v_quantum_annealing
$ python -m autopep8 --in-place --aggressive --aggressive  --recursive ./v_quantum_annealing
$ python -m isort ./v_quantum_annealing
$ python -m black ./v_quantum_annealing
```

- Lint

```sh
$ pip-compile setup.cfg
$ pip-compile dev-requirements.in
$ pip-compile lint-requirements.in
$ pip-sync requirements.txt dev-requirements.txt lint-requirements.txt
```

```sh
$ python -m flake8
$ python -m mypy
$ python -m pyright
```

## Python Documentation 
Use Juyter Book for build documentation.   
With KaTeX    
Need: Graphviz

``` sh
$ pip-compile setup.cfg
$ pip-compile build-requirements.in
$ pip-compile doc-requirements.in
$ pip-sync requirements.txt build-requirements.txt doc-requirements.txt
```

Please place your document to `docs/tutorial`either markdown or jupyter notebook style.

```sh
$ pip install -vvv .
```

```sh 
$ jupyter-book build docs --all
```


## How to use

### Python example

```python
import v_quantum_annealing as oj
sampler = oj.SASampler()
response = sampler.sample_ising(h={0: -1}, J={(0,1): -1})
response.states
# [[1,1]]

# with indices
response = sampler.sample_ising(h={'a': -1}, J={('a','b'): 1})
[{index: s for index, s in zip(response.indices, state)} for state in response.states]
# [{'b': -1, 'a': 1}]
```

## Community

- [v_quantum_annealing Slack](https://join.slack.com/t/v_quantum_annealing/shared_invite/enQtNjQyMjIwMzMwNzA4LTQ5MWRjOWYxYmY1Nzk4YzdiYzlmZjIxYjhhMmMxZjAyMzE3MDc1ZWRkYmI1YjhkNjRlOTM1ODE0NTc5Yzk3ZDA)

## About us

This product is maintained by Jij Inc.

**Please visit our website for more information!**
https://www.j-ij.com/

### Licences

Copyright 2023 Jij Inc.

Licensed under the Apache License, Version 2.0 (the "License");\
you may not use this file except in compliance with the License.\
You may obtain a copy of the License at

```
 http://www.apache.org/licenses/LICENSE-2.0  
```

Unless required by applicable law or agreed to in writing, software\
distributed under the License is distributed on an "AS IS" BASIS,\
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\
See the License for the specific language governing permissions and\
limitations under the License.
