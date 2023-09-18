r"""JAPI Client Utilities.

Provide output methods `jprint` and `jformat` for JAPI requests (*req*) and responses (*resp*).

The following examples will work with the following example request and response:

    >>> req = {'japi_request': 'get_temperature', 'japi_request_no': 123456, 'args': {'unit': 'celsius'}}
    >>> resp = {'japi_response': 'get_temperature', 'japi_request_no': 123456, 'data': {'temperature': 17.0}}
    >>> resp_incl_args = {'japi_response': 'get_temperature', 'data': {'temperature': 17.0}, 'args': {'unit': 'celsius'}, 'japi_request_no': 123456}

By default, rformat will use `_FORMAT_DEFAULT` and add escape sequences for color highlights:

    >>> jprint(req) # doctest: +SKIP
    > \033[33mget_temperature\033[0m(\033[92munit\033[0m=\033[94m"celsius"\033[0m) \033[2m#123456\033[0m

To disable colorization for individual strings, provide the following argument to `jformat` or `jprint`:

    >>> jprint(req, colorize=False)
    > get_temperature(unit="celsius") #123456

Besides color, there are several output formats to choose from. The default one, ``FORMAT='oneline'``,
as you have already seen, will parse JAPI messages and replace textual with visual elements, where
appropriate:

    - requests and responses are distinguished via prefixes ('>' for outgoing requests, '<' for incoming responses)
    - arguments are transformed to look like parameters of a method call, with the japi command as method name.
    - request number is displayed with leading '#'
    - if response, data is appended at the end

    >>> jprint(req, colorize=False)
    > get_temperature(unit="celsius") #123456
    >>> jprint(resp_incl_args, colorize=False)
    < get_temperature(unit="celsius") #123456 --> temperature=17.0


If you want to use less horizontal space, use ``FORMAT='multiline'``:

    >>> jprint(resp, fmt='multiline', colorize=False)
    < get_temperature() #123456
      temperature=17.0

Additionally output are include *indent*, *data*, *values* and *none*:

    >>> jprint(resp, fmt='indent', colorize=False)
    {
      "japi_response": "get_temperature",
      "japi_request_no": 123456,
      "data": {
        "temperature": 17.0
      }
    }
    >>> jprint(resp, fmt='data', colorize=False)
    {"temperature": 17.0}
    >>> jprint(resp, fmt='values', colorize=False)
    17.0
"""

import json
import logging as log

DIM = "\033[2m"
Y = YELLOW = "\033[33m"
G = GREEN = "\033[92m"
B = BLUE = "\033[94m"
DEFAULT = "\033[39m"
X = RESET = "\033[0m"

PREFIX_SENT = "> "
PREFIX_RCV = "< "

FORMATS = {
    "multiline": {
        "desc": "display complete message in human-readable format",
        "fmt": "{prefix}{type}({args}){msg_id}{data_parsed_newlines}",
    },
    "oneline": {
        "desc": "display important parts of message on single line",
        "fmt": "{prefix}{type}({args}){msg_id} --> {data_parsed_oneline}",
        "fmt_japi_request": "{prefix}{type}({args}){msg_id}",
        "fmt_japi_pushsrv": "{prefix}{type}({args}) --> {data_parsed_oneline}",
    },
    "indent": {
        "desc": "indented json with color",
        "fmt": "{c_on}{json_indented}{c_off}",
    },
    "data": {
        "desc": "display only response data",
        "fmt_japi_request": "",
        "fmt": "{data}",
    },
    "values": {
        "desc": "display only response data values",
        "fmt": "{values}",
    },
    "none": {
        "desc": "no formatting at all",
        "fmt": "{json}",
    },
}
"""All formats supported by :func:`jformat`."""

_FORMAT_DEFAULT = "oneline"
"""Fallback when `FORMAT` is set to unknown format."""

COLORIZE = True
FORMAT = _FORMAT_DEFAULT
"""Format used by `jformat`."""


def rtype(r: dict) -> str:
    """Return japi message type (e.g. 'japi_request', 'japi_response').

    >>> rtype({'japi_response': 'get_temperature'})
    'japi_response'

    >>> rtype({})
    Traceback (most recent call last):
    ...
    ValueError: empty japi message does not have a type!
    """
    if not r:
        raise ValueError("empty japi message does not have a type!")
    try:
        return [k for k in r if k not in ("japi_request_no", "data", "args")][0]
    except IndexError as e:
        raise ValueError(f"unknown japi response type: {r}") from e


def _prefix(r: dict) -> str:
    return PREFIX_SENT if rtype(r) == "japi_request" else PREFIX_RCV


def _color_for_msg_type(r: dict):
    """Return `GREEN` for japi_requests, `YELLOW` otherwise."""
    return _(GREEN) if rtype(r) == "japi_request" else _(YELLOW)


def _(color: str = "") -> str:
    """Conditionally add escape sequences for string highlighting."""
    return color if COLORIZE else ""


def jprint(r, fmt: str = None, colorize: str = None, *args, **kwargs):
    """Pretty-print JAPI packages."""
    print(jformat(r, fmt=fmt, colorize=colorize), *args, **kwargs)


def jformat(r, fmt: str = None, colorize: bool = None) -> str:
    """Format japi message *r* according to :py:data:`~pyjapi.util.FORMAT`."""
    if not r:
        return ""

    fmt = _handle_fmt(fmt)

    global COLORIZE
    colorize_original_value = COLORIZE
    if colorize is not None:
        COLORIZE = colorize
        log.debug(
            f'Colorization turned {"on" if colorize else "off"} for this string...'
        )

    o = (
        FORMATS[fmt]
        .get(f"fmt_{rtype(r)}", FORMATS[fmt]["fmt"])
        .format(
            json=json.dumps(r),
            json_indented=json.dumps(r, indent=2),
            data=json.dumps(r.get("data")),
            data_parsed_newlines=("\n  " if "data" in r else "")
            + "\n  ".join(
                f"{_(G)}{k}{_(X)}={_(B)}{json.dumps(v)}{_(X)}"
                for k, v in r.get("data", {}).items()
            ),
            data_parsed_oneline=", ".join(
                f"{_(G)}{k}{_(X)}={_(B)}{json.dumps(v)}{_(X)}"
                for k, v in r.get("data", {}).items()
            ),
            args=", ".join(
                f"{_(G)}{k}{_(X)}={_(B)}{json.dumps(v)}{_(X)}"
                for k, v in r.get("args", {}).items()
            ),
            type=f"{_(Y)}{r[rtype(r)]}{_(X)}",
            msg_id=f" {_(DIM)}#{r['japi_request_no']}{_(X)}"
            if "japi_request_no" in r
            else "",
            values=", ".join(f"{v}" for k, v in r.get("data", {}).items()),
            c_on=_color_for_msg_type(r),
            c_off=_(X),
            c_type=_(YELLOW),
            prefix=_prefix(r),
        )
    )

    COLORIZE = colorize_original_value
    return o


def _handle_fmt(fmt):
    if fmt is None:
        global FORMAT
        if FORMAT in FORMATS:
            fmt = FORMAT
        else:
            log.warning(
                "FORMAT='%s' is not a supported format! Will revert to default format '%s'.",
                FORMAT,
                _FORMAT_DEFAULT,
            )
            FORMAT = fmt = _FORMAT_DEFAULT
    elif fmt not in FORMATS:
        log.warning("fmt='%s' is not a supported format!", fmt)
        fmt = FORMAT
    return fmt


if __name__ == "__main__":
    r = {"japi_response": "get_temperature"}
    jprint(r, fmt="bla")
