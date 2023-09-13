"""
A module for updating project sources.
"""

# built-in
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict

# third-party
from git import Repo  # type: ignore
from git.exc import GitCommandError

# internal
from userfs.config import ProjectSpecification


def update(
    root: Path,
    project: ProjectSpecification,
    interaction_options: Dict[str, Any],
    _: Dict[str, Any],
) -> None:
    """Update an individual project."""

    repo = Repo(project.location(root=root))

    remote_name = interaction_options.get("remote", "origin")
    if remote_name in repo.remotes:
        remote = repo.remotes[remote_name]
        with suppress(GitCommandError):
            remote.pull()
