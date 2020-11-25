<p align="center">
  <img src="https://raw.githubusercontent.com/PureFunctor/amalgam-lisp/develop/docs/logo.png"></img>
</p>

<p align="center">
  LISP-like interpreted language implemented in Python.
</p>

<p align="center">
  <a href="https://github.com/PureFunctor/amalgam-lisp/actions">
    <img src="https://img.shields.io/github/workflow/status/PureFunctor/amalgam-lisp/Tests?logo=github&style=flat-square">
    </a>
  <a href="https://codecov.io/gh/PureFunctor/amalgam-lisp/">
    <img src="https://img.shields.io/codecov/c/gh/purefunctor/amalgam-lisp?label=codecov&logo=codecov&style=flat-square">
  </a>
  <a href="https://amalgam-lisp.readthedocs.io/">
    <img src="https://img.shields.io/readthedocs/amalgam-lisp?style=flat-square">
  </a>
  <a href="https://pypi.org/project/amalgam-lisp/">
    <img src="https://img.shields.io/pypi/v/amalgam-lisp?style=flat-square">
  </a>
  <a href="https://pypi.org/project/amalgam-lisp/">
    <img src="https://img.shields.io/pypi/pyversions/amalgam-lisp?style=flat-square" >
  </a>
</p>

# Installation & Basic Usage
This package can be installed through PyPI:
```bash
$ pip install amalgam-lisp
```
This makes the `amalgam` command-line script available.
```bash
$ amalgam                     # To invoke the REPL
$ amalgam hello.am            # To load and run a file
$ amalgam --expr="(+ 42 42)"  # To evaluate an expression
```

# Development Setup
Install the following dependencies:
* Python 3.7 & 3.8
* [Poetry](https://python-poetry.org)
* [Nox](https://nox.thea.codes/en/stable/) (Optional)

Clone and then navigate to the repository:
```bash
$ git clone https://github.com/PureFunctor/amalgam-lisp.git
$ cd amalgam-lisp
```

Install the dependencies for the project:
```bash
$ poetry install
$ poetry run pre-commit install
```

## Running Tests / Coverage Reports / Building Documentation
This project uses `nox` for automating various tasks like running tests and building documentation.
```
$ nox
```

Alternatively, tests, coverage reports, and the documentation can be generated manually.
```bash
$ poetry run coverage run -m pytest
$ poetry run coverage report -m
$ poetry run coverage html
$ poetry run sphinx-build docs docs/build
```
