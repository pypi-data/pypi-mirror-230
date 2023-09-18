# pyjapi - Python JAPI Client

[![Using Hatch](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Getting Started

```sh
pip install pyjapi
```

Alternatively, you might want to clone the project and go from there:

```sh
git clone git@github.com:Fraunhofer-IIS/pyjapi.git
pip install -e pyjapi/.
```

## Usage

`japi [--host HOSTNAME] [--port N] [--format FORMAT_NAME] [-v] (list|listen|request)`

## Examples

### Issue individual JAPI commands

- `japi request <JAPI_COMMAND>`

  ```console
  $ japi request get_temperature
  > get_temperature() #2a96d8
  < get_temperature() #2a96d8 --> temperature=17.0
  ```

- `japi request <COMMAND> [PARAMETERS]`

  ```console
  $ japi request get_temperature unit=kelvin
  > get_temperature(unit="kelvin") #02c6fa
  < get_temperature(unit="kelvin") #02c6fa --> temperature=290.0
  ```

### List available push services

- `japi list`

  ```console
  $ japi list
  > japi_pushsrv_list() #4fae82
  < japi_pushsrv_list() #4fae82 --> services=["push_temperature"]
  ```

### Listen to JAPI push services

- `japi listen <PUSH_SERVICE_NAME> <N_PACKAGES>`

  ```console
  $ japi listen push_temperature 3
  > japi_pushsrv_subscribe(service="push_temperature") #b71d22
  < push_temperature() --> temperature=24.833269096274833
  < push_temperature() --> temperature=25.414709848078964
  < push_temperature() --> temperature=25.912073600614352
  ```
