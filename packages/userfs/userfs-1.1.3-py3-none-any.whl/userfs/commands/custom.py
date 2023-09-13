"""
An entry-point for the 'custom' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from userfs.commands.common import add_common, run_command
from userfs.config import ProjectInteraction


def custom_cmd(args: _Namespace) -> int:
    """Execute the custom command."""
    return run_command([ProjectInteraction.CUSTOM], args)


def add_custom_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add custom-command arguments to its parser."""
    add_common(parser)
    return custom_cmd
