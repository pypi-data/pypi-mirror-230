import logging

import click

from cronpar.api import explain
from cronpar.handler import validate_input

_logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def root():
    """Command-line interface."""
    pass


@root.command("explain")
@click.argument("cron", nargs=1)
def run_explain(cron: str):
    cron_list = cron.split(" ")
    validate_input(cron_list)
    explain(cron_list)


def main():
    root()


if __name__ == "__main__":
    main()
