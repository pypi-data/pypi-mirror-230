"""
A module for fetching projects.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from git import Repo  # type: ignore
from vcorelib.paths import rel

# internal
from userfs.config import ProjectSpecification, SourceKind


def fetch(
    root: Path,
    project: ProjectSpecification,
    interaction_options: Dict[str, Any],
    _: Dict[str, Any],
) -> None:
    """Fetch an individual project."""

    location = project.location(root=root)

    if project.source.kind is SourceKind.GIT:
        # Clone the repository.
        if not location.is_dir():
            url = project.url
            Repo.clone_from(project.url, location, **interaction_options)
            project.logger.info(
                "Cloned from '%s' (%s).", url, interaction_options
            )

        repo = Repo(project.location(root=root))

        # Update submodules if specified.
        if "submodules" in project.attributes:
            for submodule in repo.submodules:
                submodule.update(
                    recursive=project.attributes["submodules"].get(
                        "recursive", False
                    )
                )

    project.logger.info("Location: '%s'.", rel(location))
