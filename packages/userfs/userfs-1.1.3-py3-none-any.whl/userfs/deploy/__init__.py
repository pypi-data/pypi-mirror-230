"""
A module for deploying project sources.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# internal
from userfs.config import ProjectSpecification


def deploy(
    root: Path,
    project: ProjectSpecification,
    interaction_options: Dict[str, Any],
    cli_options: Dict[str, Any],
) -> None:
    """Deploy an individual project."""

    print(root)
    print(project)
    print(interaction_options)
    print(cli_options)
