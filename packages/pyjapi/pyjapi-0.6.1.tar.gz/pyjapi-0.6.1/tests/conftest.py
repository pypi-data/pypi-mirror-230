import pathlib
import subprocess
from time import sleep

import pytest

from pyjapi import JAPIClient

root = pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def server():
    server_bin = root / "ext" / "pylibjapi" / "pylibjapi.py"
    proc = subprocess.Popen(
        [server_bin],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env={"LIBJAPI_PORT": "1234"},
    )
    # wait for server to be ready
    sleep(1)

    # print(proc.stdout.readline())
    yield

    proc.kill()


@pytest.fixture(scope="session")
def client():
    try:
        client = JAPIClient()
    except Exception:
        pytest.xfail("No backend available!")
    yield client


@pytest.fixture(autouse=True)
def add_japi_client(doctest_namespace, client):
    doctest_namespace["japi_client"] = client
