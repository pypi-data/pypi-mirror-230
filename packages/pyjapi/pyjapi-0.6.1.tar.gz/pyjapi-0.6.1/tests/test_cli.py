from click.testing import CliRunner, Result

from pyjapi import __version__, cli


def test_version_displays_library_version():
    """Test `ciu --version` flag."""
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli, ["--version"])
    assert (
        __version__ in result.output.strip()
    ), "Version number should match library version."


def test_no_command_prints_help():
    """Test `ciu` prints help if no subcommand is given."""
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli)
    assert result.output.startswith(
        "Usage"
    ), "If no subcommand is given, help should be printed."
