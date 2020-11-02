# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

* Changed deferred functions/macros to unquote unevaluated arguments.

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
