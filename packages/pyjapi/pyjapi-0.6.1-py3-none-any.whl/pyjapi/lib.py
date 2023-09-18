#!/usr/bin/env python3
"""JAPI Client in Python."""

import json
import logging as log
import socket
import typing as t
import uuid

import strconv

from ._types import JAPIRequest, JAPIResponse


class JAPIClient:
    """Connect and interact with arbitrary libJAPI-based backend."""

    def __init__(
        self,
        address: t.Tuple[str, int] = ("localhost", 1234),
        timeout: int = 3,
        request_no: t.Union[int, bool] = False,
    ):
        """Create new JAPIClient object.

        Args:
            address: Tuple of host (str) and port (int). Defaults to ('localhost', 1234).
            timeout: Timeout for requests in seconds. Defaults to 5.
            request_no:
                Whether to include japi request number.
                If a positive integer is given, request number starts at given integer and will increment with each message.
                If `True` is given, :py:func:`uuid.uuid4` is used to generate a random request number with 6 characters.
        """
        self._request_no = request_no
        self.last_request = None
        self.address = address
        try:
            self.sock = socket.create_connection(self.address)
            self.sock.settimeout(timeout)
            self.sockfile = self.sock.makefile()
        except Exception as e:
            raise (e)

    @property
    def request_no(self) -> t.Union[bool, int, str]:
        """Returns suitable *japi_request_no* or `False`, if none should be used."""
        if isinstance(self._request_no, bool):
            return str(uuid.uuid4())[:6] if self._request_no else False
        elif isinstance(self._request_no, int):
            self._request_no += 1
            return self._request_no - 1

    def list_push_services(self, unpack=True):
        """List available JAPI push services.

        Examples:
            >>> japi_client.list_push_services()
            ['push_temperature']

            >>> japi_client.list_push_services(unpack=False)
            {'japi_response': 'japi_pushsrv_list', 'data': {'services': ['push_temperature']}}

        Returns: List of available push services
        """
        r = self.query("japi_pushsrv_list")
        if unpack:
            r = r.get("data", {}).get("services", [])
        return r

    def query(self, cmd: str, **kwargs) -> dict:
        """Query JAPI server and return response.

        If an error occurred, an empty dictionary is returned.

        Returns:
            Response object
        """
        msg_request = JAPIRequest(self._build_request(cmd, **kwargs))
        log.debug("> %s", msg_request.dumps())

        return self._request(msg_request)

    def listen(self, service: str, n_messages: int = 0) -> dict:
        """Listen for *n* values of *service*.

        Args:
            service: name of push service
            n_messages: number of messages to listen for (optional, defaults to 0)

        Returns:
            Push service messages
        """
        self._subscribe(service)
        log.info(
            f"Listening for {f'{n_messages} ' if n_messages > 0 else ''}'{service}' package{'s' if n_messages != 1 else ''}..."
        )
        for n, line in enumerate(self.sock.makefile(), start=1):
            yield json.loads(line)
            if n_messages and n >= n_messages:
                break
        self._unsubscribe(service)

    def _subscribe(self, service):
        """Subscribe to JAPI push service."""
        log.info("Subscribing to '%s' push service.", service)
        return self.query("japi_pushsrv_subscribe", service=service)

    def _unsubscribe(self, service):
        """Unsubscribe from JAPI push service."""
        log.info("Unsubscribing from '%s' push service.", service)
        return self.query("japi_pushsrv_unsubscribe", service=service)

    def _build_request(self, cmd, **kwargs):
        request = {"japi_request": cmd}
        if self.request_no:
            request["japi_request_no"] = self.request_no

        if kwargs := {k: convert(v) for k, v in kwargs.items()}:
            request["args"] = kwargs

        self.last_request = request
        return request

    def _request(self, japi_request: JAPIRequest) -> JAPIResponse:
        json_cmd = json.dumps(japi_request) + "\n"
        try:
            self.sock.sendall(json_cmd.encode())
            resp = self.sockfile.readline()
            log.debug("< %s", resp)
        except (socket.gaierror, ConnectionError):
            log.warning("'%s:%d' is not available", self.address[0], self.address[1])
            return {}
        except socket.timeout:
            log.info("Request Timeout!")
            return {}
        except Exception as e:
            log.info(str(e))
            return {}

        try:
            response = json.loads(resp)
            response = JAPIResponse(response)
        except json.JSONDecodeError as e:
            log.error("Cannot parse response: %s (%s)", resp, str(e))
            return {}

        return response

    def __del__(self):
        """Close socket upon deletion."""
        if hasattr(self, "sock"):
            if self.sockfile:
                self.sockfile.close()
            self.sock.close()


def convert(v: str) -> t.Any:
    """Cast v to appropriate type."""
    return strconv.convert(convert_numbers(v))


def convert_numbers(v):
    """Convert string numbers other than base 10 to base 10.

    Examples:
        >>> convert_numbers('0b10001')
        '17'
        >>> convert_numbers('0o21')
        '17'
        >>> convert_numbers('0x11')
        '17'
    """
    if isinstance(v, str):
        if v.lower().startswith("0x"):
            return str(int(v[2:], base=16))
        if v.lower().startswith("0o"):
            return str(int(v[2:], base=8))
        if v.lower().startswith("0b"):
            return str(int(v[2:], base=2))
    return v
