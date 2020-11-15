# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

* Added the `__iter__` and `__len__` methods for the `SExpression` and `Vector` classes.
* Changed the `Amalgam` base class to use `ABCMeta` as a metaclass instead of inheriting from `ABC`.
* Changed the `evaluate` method of `SExpression` to handle uncallable types manually.
* Changed the `located_on` method of `Located` to type check for subclasses.
* Changed function organization for `primordials.py`, opting into making it a subpackage.
* Removed `bind` and `call` from `Amalgam`, opting into manual checks intead.

## [0.2.0] 2020-11-13
This marks the second volative release before `v1.0.0`.

* Added the `Located` mixin dataclass for AST nodes.
* Added a `__repr__` method to `Environment`.
* Added the `name` and `engine` parameters and attributes to `Engine`.
* Added the `_interpret` and `interpret` methods to `Engine`.
* Added the `Notification` `Amalgam` subclass for representing failures.
* Added the `make_report` method for `Notification` to visualize failures.
* Added a way to keep track of the original text and its source.
* Changed deferred functions/macros to unquote unevaluated arguments.
* Changed user-facing documentation for the `macro` function.
* Changed the `env_push` method of `Environment` to propagate metadata from a parent.
* Changed the `repl` method of `Engine` to use its own parse buffer and continuation logic.
* Changed the `repl` method of `Engine` to visualize `Notification`s.
* Changed the `_loop`, `_return`, and `_break` methods to use `Notification`s.
* Fixed unnecessary imports for type checking using `TYPE_CHECKING`.
* Removed the `_require` and `_provide` built-in functions.
* Removed the `DisallowedContextError` exception.
* Removed the `SymbolNotFound` exception.
* Removed the `parse_and_run` method of `Engine`.
* Removed `Parser` in favor of the `parse` function.
* Removed type annotations for the transformer methods in `Expression`.

## [0.1.0] 2020-11-2
This marks the first volatile feature release before `v1.0.0`.

* Added implementations and tests for the following:
  * Language entities: `amalgam.amalgams`.
  * Execution environments: `amalgam.environment`.
  * Runtime engine: `amalgam.engine`.
  * Built-in functions: `amalgam.primordials`.
  * Parser built with Lark: `amalgam.parser`.
  * Command-line interface: `amalgam.cli`.
* Added user-facing and internal documentation.
* Type annotaions and runtime casts for `mypy`.
