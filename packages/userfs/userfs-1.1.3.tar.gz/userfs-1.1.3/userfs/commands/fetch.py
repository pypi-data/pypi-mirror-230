"""
An entry-point for the 'fetch' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from userfs.commands.common import add_common, run_command
from userfs.config import ProjectInteraction


def fetch_cmd(args: _Namespace) -> int:
    """Execute the fetch command."""

    interactions = [ProjectInteraction.FETCH]
    if args.update:
        interactions.append(ProjectInteraction.UPDATE)

    return run_command(interactions, args)


def add_fetch_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add fetch-command arguments to its parser."""

    add_common(parser)
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="whether or not to also attempt to update project sources",
    )

    return fetch_cmd
