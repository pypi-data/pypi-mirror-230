# pylibjapi

A libjapi server implementation in Python. It tries it's very best to act like the ADC Board.

## Purpose

This dummy backend was created to assist in the developement of the [DAC Board GUI](https://git01.iis.fhg.de/abt-hfs/interstellar/gui_fe_dac). It shouldn't be difficult however to adapt this for usage in other JAPI projects.

## Getting Started

### Requirements

* websocketd
* Python3
* socat

### Usage

**Start pylibjapi**
```sh
$ make
Fri, 28 May 2021 14:01:49 +0200 | INFO   | server     |  | Serving using application   : /usr/local/bin/socat - TCP4:localhost:1234
Fri, 28 May 2021 14:01:49 +0200 | INFO   | server     |  | Starting WebSocket server   : ws://0.0.0.0:8081/
Starting pylibjapi
```

**Note:** You can restart pylibjapi by simply calling `make` again. It will automatically kill any running instances before starting new ones.

**Stop pylibjapi**
```sh
$ make kill
./japi2ws: line 14: 17785 Terminated: 15          websocketd --port=$WS_PORT -address $WS_HOST socat - TCP4:$JAPI_HOST:$JAPI_PORT

Terminating pylibjapi, closing socket. Bye o/
```

#### Standalone (without `websocketd`)

```sh
$ ./pylibjapi.py
Starting pylibjapi
^C
Terminating pylibjapi, closing socket. Bye o/
```

`pylibjapi` can be terminated with `CTRL + C` or by sending a Unix `SIGTERM` signal, for example with `pkill -SIGTERM -f pylibjapi.py`

## Features

- Answers to JAPI request received on `localhost:1234`
  - it is also possible to provide different host and port data using the environment variables `LIBJAPI_HOST` and `LIBJAPI_PORT`
- The emulated board state data can be viewed in real time (for example with VS Code) by opening `state_data.tmp.json`
  - Note: `state_data.tmp.json` is copied from `state_data.json` when the server is started. Changes by set requests do not affect `state_data.json`
- `args` are taken into account according to the specification. They are also send back with the answer.
- `japi_request_no` is supported

## Adding commands

- data points corresponding to `get` or `set` requests are provided by the `state_data.json` file
- `state_data.json` provides the *default* return value for a data point - this value can be changed by set requests
- Naming Convention:
  - Command `get_controlbits` or `set_controlbits` -> data point is called `controlbits`
- The different return options according to given `args` are represented in layers in the JSON File

Example - `controlbits` in `state_data.json`:

```json
  "controlbits": {
    "DEVICE": {
      "1": {
        "CONTROLBIT": {
          "1": {
            "FUNCTIONALITY": "inrange"
          },
          "2": {
            "FUNCTIONALITY": "trig"
          }
        }
      },
      "2": {
        "CONTROLBIT": {
          "1": {
            "FUNCTIONALITY": "timestamp"
          },
          "2": {
            "FUNCTIONALITY": "parity"
          }
        }
      }
    }
  }
```
