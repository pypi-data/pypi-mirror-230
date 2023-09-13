# =====================================
# generator=datazen
# version=3.1.2
# hash=c3b94c7c029203ccd0bc061a0024237d
# =====================================

"""
A module aggregating package commands.
"""

# built-in
from typing import List as _List
from typing import Tuple as _Tuple

# third-party
from vcorelib.args import CommandRegister as _CommandRegister

# internal
from userfs.commands.build import add_build_cmd
from userfs.commands.custom import add_custom_cmd
from userfs.commands.fetch import add_fetch_cmd


def commands() -> _List[_Tuple[str, str, _CommandRegister]]:
    """Get this package's commands."""

    return [
        (
            "build",
            "attempt to build a software project from its sources",
            add_build_cmd,
        ),
        (
            "custom",
            "perform a custom interaction, sourced from external hooks",
            add_custom_cmd,
        ),
        (
            "fetch",
            "attempt to obtain some software from the internet",
            add_fetch_cmd,
        ),
        ("noop", "command stub (does nothing)", lambda _: lambda _: 0),
    ]
