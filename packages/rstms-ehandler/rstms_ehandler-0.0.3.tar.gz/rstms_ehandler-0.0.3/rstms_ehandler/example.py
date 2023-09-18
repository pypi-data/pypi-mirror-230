"""Example click cli for rstms_ehandler."""

import logging
import sys

import click

from rstms_ehandler import set_ehandler_option


def init_logger(ctx, option, logger):
    if logger:
        logging.basicConfig(level=logger)
        logger = logging.getLogger(__name__)
    set_ehandler_option(ctx, option, logger)
    return logger


@click.command("ehandler")
@click.option("-f", "--fail", is_flag=True, help="raise exception")
@click.option(
    "-d",
    "--debug",
    is_eager=True,
    is_flag=True,
    callback=set_ehandler_option,
    help="output stack trace on excption",
)
@click.option(
    "-l",
    "--logger",
    is_eager=True,
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    callback=init_logger,
    help="log exceptions to logger",
)
@click.option(
    "-p",
    "--pdb",
    is_eager=True,
    is_flag=True,
    callback=set_ehandler_option,
    help="break into postmortem debugger on exception",
)
@click.option("-v", "--verbose", is_flag=True, help="show options")
@click.pass_context
def cli(ctx, debug, fail, logger, pdb, verbose):
    """example click CLI for rstms_ehandler"""
    if verbose:
        click.echo(f"{debug=}")
        click.echo(f"{fail=}")
        click.echo(f"{logger=}")
        click.echo(f"{pdb=}")
        click.echo(f"{verbose=}")
        click.echo(f"ehandler={ctx.obj['ehandler']}")
    if fail:
        raise FileNotFoundError("nonexistent_file")
    if logger:
        logger.warning("warning message")
    if ctx.obj.get("logger"):
        ctx.obj["logger"].info("info message")
    click.echo("success")


if __name__ == "__main__":
    sys.exit(cli())
