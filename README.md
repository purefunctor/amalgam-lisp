# amalgam-lisp [![Travis CI](https://img.shields.io/travis/com/purefunctor/amalgam-lisp?label=build&logo=travis&style=flat-square)](https://travis-ci.com/github/PureFunctor/amalgam-lisp) [![Codecov](https://img.shields.io/codecov/c/gh/purefunctor/amalgam-lisp?label=codecov&logo=codecov&style=flat-square)](https://codecov.io/gh/PureFunctor/amalgam-lisp/)

Lisp-like interpreted language implemented in Python.

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

## Running Tests / Coverage Reports
The preferred way of running tests is through `tox`, which generates coverage data for Python 3.7 and 3.8 that can then be combined:
```bash
$ poetry run tox
$ poetry run coverage combine
```

In order to view reports for the coverage data:
```bash
$ poetry run coverage html
$ poetry run coverage report -m
```
