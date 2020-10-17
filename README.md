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
`tox` is used for the automation of the execution of tests, which generates, combines, and reports coverage data for Python 3.7 and 3.8.
```bash
$ poetry run tox
```

Alternatively, tests and coverage reports can be generated manually.
```bash
$ poetry run coverage run -m pytest
$ poetry run coverage combine
$ poetry run coverage report -m
$ poetry run coverage html
```
