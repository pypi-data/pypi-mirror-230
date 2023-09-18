import logging as log
import socket

import pytest

from pyjapi.lib import JAPIClient, convert


@pytest.mark.parametrize(
    "cmd",
    [
        "japi_pushsrv_list",
        "japi_pushsrv_subscribe",
        "japi_pushsrv_unsubscribe",
    ],
)
def test_pushsrv_commands(client, cmd):
    r = client.query(cmd)
    log.info(r)
    assert isinstance(r, dict)
    assert r["japi_response"] == cmd


def test_client_no_server_at_address():
    with pytest.raises((ConnectionError, socket.gaierror)):
        JAPIClient(("someServer", 8989), timeout=0.1)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("some_string", "some_string"),
        ("false", False),
        ("1000", 1000),
        ("1.2", 1.2),
        ("1e4", 10000.0),
        ("-inf", float("-inf")),
    ],
)
def test_type_inference(value, expected):
    """Test type inference is working."""
    result = convert(value)
    assert result == expected
