# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* `__iter__` and `__len__` for `SExpression` and `Vector`.
* Special `&rest` syntax for `fn`, `mkfn`, and `macro` through `createfn`.
* `AmalgamMeta` to be used by `Amalgam` instead of inheriting from `ABC`.
* `Failure` and `FailureStack` to implement a notification framework through `AmalgamMeta`.

### Changed
* Manually handle uncallable types in `SExpression.evaluate`.
* Account for subclasses when type checking `Located.located_on`.
* Reorganize `primordials.py`, transforming it into a subpackage.
* Refactor internal code to use the new notification framework.

### Removed
* The `bind` and `call` methods from `Amalgam`, favoring manual checks instead.
* The `Internal`, `Trace`, and `Notification` classes in favor of `Failure` and `FailureStack`.


## [0.2.0] 2020-11-13
This marks the second volative release before `v1.0.0`.

### Added
* `Located` mixin dataclass for AST nodes.
* `__repr__` for `Environment`.
* `name` and `engine` parameters and attributes to `Engine`.
* `_interpret` and `interpret` methods to `Engine`.
* `Notification` class for representing failures.
* Tracking of the original text and its source during parsing and evaluation.

### Changed
* Unquote unevaluated arguments in deferred functions and macros.
* Update user-facing documentation for the `macro` function.
* Move parse buffer and continuation logic to `Engine.repl`.
* Visualize `Notification`s in `Engine.repl`.
* Use `Notification`s in `_loop`, `_return`, and `_break`.

### Fixed
* Unnecessary imports for type checking.

### Removed
* The `_require` and `_provide` built-in functions.
* The `DisallowedContextError` exception.
* The `SymbolNotFound` exception.
* The `parse_and_run` method of `Engine`.
* The `Parser` class in favor of the `parse` function.
* Type annotations for the transformer methods in `Expression`.


## [0.1.0] 2020-11-2
This marks the first volatile feature release before `v1.0.0`.

### Added
* Implementations and tests for the following:
  * Language entities: `amalgam.amalgams`.
  * Execution environments: `amalgam.environment`.
  * Runtime engine: `amalgam.engine`.
  * Built-in functions: `amalgam.primordials`.
  * Parser built with Lark: `amalgam.parser`.
  * Command-line interface: `amalgam.cli`.
* User-facing and internal documentation.
* Type annotaions and runtime casts for `mypy`.
