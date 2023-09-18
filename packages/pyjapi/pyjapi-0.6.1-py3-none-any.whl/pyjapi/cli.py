#!/usr/bin/env python3
"""Command Line Interface for :py:class:`pyjapi.lib.JAPIClient`.

Tip:
    For a documentation of all cli commands and options, see :ref:`cli`
"""

import logging as log
import os
import sys

import click

from pyjapi import lib, util

__version__ = "0.6.1"

CTX_SETTINGS = dict(auto_envvar_prefix="JAPI")

HOST = os.getenv("JAPI_HOST", "localhost")
PORT = int(os.getenv("JAPI_PORT", 1234))


def complete_service(ctx, args, incomplete):
    """Complete push services registered with the backend."""
    # new JAPIClient instance used for autocompletion, as click.ctx doesn't exist yet
    try:
        client = lib.JAPIClient((HOST, PORT))
        services = client.list_push_services()
        if incomplete:
            services = [s for s in services if s.startswith(incomplete)]
        return services
    except Exception:
        return []


def complete_format(ctx, args, incomplete):
    """Complete ``--format`` option."""
    return [
        click.shell_completion.CompletionItem(fmt_name, help=fmt["desc"])
        for fmt_name, fmt in util.FORMATS.items()
        if not incomplete or fmt_name.startswith(incomplete)
    ]


# You cannot do any output to stdout in callbacks (will mess with autocompletion)
def _callback_format(ctx, param, value):
    """Set `pyjapi.util.FORMAT` to *value* (if supported)."""
    util.FORMAT = value
    return value


@click.group(invoke_without_command=True, context_settings=CTX_SETTINGS)
@click.option(
    "-h",
    "--host",
    default="localhost",
    allow_from_autoenv=True,
    help="JAPI server hostname or ip",
    type=click.STRING,
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    default=1234,
    allow_from_autoenv=True,
    help="JAPI server port",
    type=click.INT,
    show_default=True,
)
@click.option(
    "-f",
    "--format",
    default="oneline",
    allow_from_autoenv=True,
    help="Output format of JAPI messages",
    shell_complete=complete_format,
    type=click.STRING,
    show_default=os.getenv("JAPI_FORMAT") if "JAPI_FORMAT" in os.environ else True,
    callback=_callback_format,
    expose_value=False,
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    allow_from_autoenv=True,  # this doesn't work for this option
    show_default=os.getenv("JAPI_VERBOSE") if "JAPI_VERBOSE" in os.environ else True,
    default=0,
    help="Increase verbosity of output.",
    type=click.INT,
)
@click.version_option(__version__, message="%(version)s")
@click.pass_context
def cli(ctx, host, port, verbose):
    """User & Command Line Friendly JAPI Client."""
    # If no command is given, print help and exit
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        exit(0)

    # Configure logger
    log.root.handlers = []
    log.basicConfig(
        stream=sys.stderr,
        level=[log.WARN, log.INFO, log.DEBUG][verbose]
        if 0 <= verbose < 2
        else log.DEBUG,
        format="%(message)s",
    )

    if ctx.invoked_subcommand not in ["completions"]:
        log.info(f"Talking to {host}:{port}")
        try:
            ctx.obj = lib.JAPIClient(address=(host, port), request_no=True)
        except Exception:
            click.secho(f"{host}:{port} is not available!", fg="red")
            exit(1)


@cli.command()
@click.argument("service", default="push_temperature", shell_complete=complete_service)
@click.argument("n", default=0, type=click.INT)
@click.pass_context
def listen(ctx, service, n):
    """Listen for values of push service.

    If no SERVICE is given, SERVICE defaults to 'push_temperature' (available in libjapi-demo).
    For a list of available SERVICEs, use::

        $ japi list

    By default, values are continuously received until either server or client closes the
    connection. Provide a positive integer for N to stop listening after N values have been
    received.
    """
    for i, response in enumerate(ctx.obj.listen(service, n)):
        if i == 0 and util.jformat(ctx.obj.last_request):
            click.echo(util.jformat(ctx.obj.last_request))
        click.echo(util.jformat(response))


@cli.command()
@click.pass_context
def list(ctx):
    """List available push services."""
    resp = ctx.obj.list_push_services(unpack=False)
    if util.jformat(ctx.obj.last_request):
        click.echo(util.jformat(ctx.obj.last_request))
    click.echo(util.jformat(resp))


@cli.command()
@click.argument("cmd")
@click.argument("parameters", nargs=-1)
@click.option("-r", "--raw", is_flag=True, default=False, help="print raw response")
@click.pass_context
def request(ctx, cmd, parameters, raw):
    """Issue individual JAPI request.

    CMD is the JAPI Command (e.g. get_temperature) followed by any additional PARAMETERS.
    Parameters might be key-value-pairs in the form: key=value

    **Example**: Request *temperature* value in Kelvin

    .. code-block:: console

       $ japi request get_temperature unit=kelvin
       > get_temperature(unit="kelvin") #d8564d
       < get_temperature(unit="kelvin") #d8564d --> temperature=290.0
    """
    # Convert tuple of parameter list into dict: ('foo', 'bar=1') -> {'foo': '', 'bar': '1'}
    parameters = {
        p.split("=")[0]: p.split("=")[1] if "=" in p else "" for p in parameters
    }

    response = ctx.obj.query(cmd, **parameters)

    if request_str := util.jformat(ctx.obj.last_request):
        click.echo(request_str)

    if response:
        if raw:
            util.FORMAT = "none"
        if response_str := util.jformat(response):
            click.echo(response_str)
    else:
        click.secho("No response received!", fg="red")


completion_shells = ["bash", "zsh", "fish"]


@cli.command()
@click.argument("shell", type=click.Choice([*completion_shells, "-", ""]), default="")
def completions(shell):
    r"""Generate shell completions.

    Activate in current shell:

        eval "\`japi completions -\`"
    """
    import subprocess

    if not shell:
        click.secho(
            "To enable shell completion, run\n\n"
            '    eval "`japi completions -`"\n\n'
            "If your shell is not detected automatically, you can specify it as argument like this:\n\n"
            '    eval "`japi completions zsh`"'
        )
    elif shell == "-":
        log.debug("Trying to detect shell...")

        for idx, env_shell in enumerate(
            [
                "bash" if "BASH" in os.environ else "",
                "zsh" if "ZSH_NAME" in os.environ else "",
                os.getenv("PYENV_SHELL"),
                os.environ["SHELL"].split("/")[
                    -1
                ],  # return completions for default shell
            ],
            start=1,
        ):
            if env_shell in completion_shells:
                log.debug("Detected(%d): %s", idx, env_shell)
                shell = env_shell
                break
        else:
            raise click.UsageError(
                "Couldn't detect shell. Please specify shell as argument, like this\n\n    $ japi completions zsh"
            )

    click.echo(subprocess.getoutput(f"_JAPI_COMPLETE={shell}_source japi"))


if __name__ == "__main__":
    cli(prog_name="japi")
