<p align="center">
  <img src="./docs/logo.png"></img>
</p>

<p align="center">
  LISP-like interpreted language implemented in Python.
</p>

<p align="center">
  <img src="https://img.shields.io/travis/com/purefunctor/amalgam-lisp?label=build&logo=travis&style=flat-square" href="https://travis-ci.com/github/PureFunctor/amalgam-lisp"></img>
  <img src="https://img.shields.io/codecov/c/gh/purefunctor/amalgam-lisp?label=codecov&logo=codecov&style=flat-square" href="https://codecov.io/gh/PureFunctor/amalgam-lisp/">
</p>

# Development Setup
Install the following dependencies:
* Python 3.7 & 3.8
* [Poetry](https://python-poetry.org)

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
`nox` is used for the automation of the execution of tests, which generates, combines, and reports coverage data for Python 3.7 and 3.8, as well as building documentation for the project.
```bash
$ poetry run nox
```

Alternatively, tests, coverage reports, and the documentation can be generated manually.
```bash
$ poetry run coverage run -m pytest
$ poetry run coverage combine
$ poetry run coverage report -m
$ poetry run coverage html
$ poetry run sphinx-build docs docs/build
```
