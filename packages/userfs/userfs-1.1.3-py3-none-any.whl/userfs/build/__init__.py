"""
A module for building project sources.
"""

from __future__ import annotations

# built-in
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# third-party
from vcorelib.logging import LoggerType

# internal
from userfs.config import ProjectSpecification


def run_process(
    logger: LoggerType, args: List[str]
) -> subprocess.CompletedProcess[str]:
    """Run a command-line process."""

    logger.info("Starting %s.", args)
    result = subprocess.run(args, check=False, text=True)
    logger.info("Exited %d.", result.returncode)
    return result


def build(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Build an individual project."""

    if project.attributes.get("mk"):
        if project.attributes.get("python"):
            loc = str(project.location(root=root))
            run_process(project.logger, ["mk", "-C", loc, "dz-sync"])
            run_process(project.logger, ["mk", "-C", loc, "python-build"])
