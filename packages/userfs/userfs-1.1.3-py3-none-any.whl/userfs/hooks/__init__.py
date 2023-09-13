"""
A module implementing interfaces to interact with external scripts and modules.
"""

# built-in
from contextlib import suppress
from importlib import import_module
from logging import getLogger
from typing import Callable, Dict, Optional, Set, cast

# third-party
from vcorelib.names import to_snake

# internal
from userfs.config import Config, Interact, ProjectInteraction

HookLoader = Callable[[str, ProjectInteraction, Config], Optional[Interact]]
LOG = getLogger(__name__)


def get_hooks(
    prefixes: Set[str], project: str, interaction: ProjectInteraction
) -> Dict[str, Optional[Interact]]:
    """Attempt to load a certain kind of project hook."""

    result: Dict[str, Optional[Interact]] = {}

    for prefix in prefixes:
        result[prefix] = None
        with suppress(ModuleNotFoundError):
            mod_name = f"{to_snake(project)}_hooks"
            LOG.info("Looking for '%s' module.", mod_name)
            mod = import_module(mod_name)

            hook_name = f"{prefix}_{interaction.value}"
            LOG.info("Looking for '%s' hook.", hook_name)
            result[prefix] = cast(Interact, getattr(mod, hook_name, None))

    return result
