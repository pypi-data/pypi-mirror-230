"""
An entry-point for the 'build' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from userfs.commands.common import add_common, run_command
from userfs.config import ProjectInteraction


def build_cmd(args: _Namespace) -> int:
    """Execute the build command."""

    interactions = [ProjectInteraction.BUILD]
    if args.deploy:
        interactions.append(ProjectInteraction.DEPLOY)

    return run_command(interactions, args)


def add_build_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add build-command arguments to its parser."""

    add_common(parser)
    parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help=(
            "whether or not to also attempt to "
            "deploy or install the built project assets"
        ),
    )

    return build_cmd
