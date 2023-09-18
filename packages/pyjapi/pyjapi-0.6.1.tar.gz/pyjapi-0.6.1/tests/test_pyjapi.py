import pathlib
from subprocess import CompletedProcess, run


def test_execution_via_module():
    r: CompletedProcess = run(["python3", "-m", "pyjapi"], capture_output=True)
    assert r.returncode == 0
    assert r.stdout.decode().startswith("Usage: japi [OPTIONS] COMMAND [ARGS]...")
    assert r.stderr.decode() == ""


def test_direct_execution():
    r: CompletedProcess = run(
        [pathlib.Path(__file__).parent.parent / "src" / "pyjapi" / "cli.py"],
        capture_output=True,
    )
    assert r.returncode == 0
    assert r.stdout.decode().startswith("Usage: japi [OPTIONS] COMMAND [ARGS]...")
    assert r.stderr.decode() == ""
