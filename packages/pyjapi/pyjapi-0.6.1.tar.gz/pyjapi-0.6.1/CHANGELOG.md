# 👨🏼‍🚀 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [latest]

## [v0.6.1]

- Add `japi completions` command: completions can now be enabled with the following
  command

  ```sh
  eval "`japi completions -`"
  ```

- Remove completion files

### 🔩 Under the Hood

- use hatch as package manager
- use ruff for linting
- use black for formatting
- add pre-commit hooks
- demo server is now started at the beginning of each test session
- add spell checking and fix typos
- remove bumpversion config -> use `hatch version` instead

## [v0.6.0]

- Parse hexadecimal ('0x...'), octal ('0o...') and binary ('0b...') to integers
- Requests/response are not echoed when they are empty (after formatting has been
  applied)
- Add `completions` command which allows to enable shell completions via `eval "\`japi
  completions -\`"`

### 🔩 Under the Hood

- Publish package in Gitlab's package registry
- Use `pyproject.toml` over `setup.py` for packaging information
- Update docs to use furo theme and myst markdown parser
- Add documentation for `pyjapi.err` module

## [v0.5.2]

- Add type inference for JAPI argument values

## [v0.5.1]

Fix issue where first JAPIClient connection, used for push service completion, was kept
alive unnecessarily long. This solves an issue encountered with pylibjapi backends, as
the first connection blocked the receiving socket, which caused a timeout in the client.

## [v0.5.0]

- Command Line Interface
  - More output formats
- Documentation
  - Add Documentation
  - Documentation can be published to Confluence for more visibility
- Fixes
  - fix response being printed twice on --raw
  - handle response timeouts gracefully (timeout after 2 seconds)
- Tests
  - Add doctests
  - Add basic cli and client tests
- CI
  - Run tests in CI Pipeline
  - Publish docs and coverage report via Gitlab Pages
- Refactoring
  - pyjapi is now a package instead of a module
  - split cli and JAPIClient

## [v0.4.0]

### 👨‍💻 User-facing changes

- Add formatting options (`-f/--format`)
- Add autocompletion for zsh users (source `pyjapi-complete.zsh` or `.env`)
- Fix issues when backend was unavailable
- Support different ways to access command line interface
  - Install package `pip install -e .` and run `japi`
  - Install package `pip install -e .` and run `python -m pyjapi`
  - Run `./src/pyjapi/cli.py` (experimental, might be deprecated soon)

### 🔩 Under the Hood

- Refactor module into package for easier maintenance
  - Extract command line interface into separate module
- Add `.env` file as example environment configuration
  - includes sourcing `pyjapi-complete.zsh` for autocompletion
- Declutter `.gitignore`

## [v0.3.1]

- Support requests with additional parameters
  - e.g. `japi request get_temperature unit=kelvin`

## [v0.3.0]

- Extend CLI
  - List available push services using `japi list`
  - Improve accessibility (help texts, argument names, option descriptions)
- Remove unused code
  - `JAPIClient.get()`: was wrapper around `JAPIClient.listen(..., n_pkgs=1)`
- Fix Issues
  - Fix error on installation due to import of version string
  - Fix error on object deletion when connection was unsuccessful
- Project Structure
  - Rename `JAPIClient.conn_str` to `JAPIClient.address`: conform with naming convention
    in `socket`
  - Move `__version__` string to `setup.py`
  - Add `libjapi-demo` as submodule for getting started with example quickly
  - Use `''` for strings uniformly (exceptions: nested f-strings, docstrings)

## [v0.2.0]

- Update to work with libjapi-demo v0.2

## [v0.1.0]

- rewrite cli in `click`
- remove pyqt5 dependency
- extend README

## [v0.0.0]

- extracted from
  [interstellar/sw_adc](https://git01.iis.fhg.de/abt-hfs/interstellar/sw_adc), based on
  [`JAPIClient.py`](https://git01.iis.fhg.de/abt-hfs/interstellar/gui_adc/-/blob/b281c0925600d76839bb11a63ef23a7433734467/gui/JAPIClient.py)
  and
  [`interstellar-cli`](https://git01.iis.fhg.de/abt-hfs/interstellar/sw_adc/-/blob/d5abdf3d22a65bee2e01c37e8bc4376278550f00/cli/interstellar-cli)

[latest]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.6.1...main
[v0.6.1]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.5.2...v0.6.0
[v0.5.2]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.5.1...v0.5.2
[v0.5.1]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.3.1...v0.4.0
[v0.3.1]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/Fraunhofer-IIS/pyjapi/compare/v0.0.0...v0.1.0
[v0.0.0]: https://github.com/Fraunhofer-IIS/pyjapi/commit/9f53a926
