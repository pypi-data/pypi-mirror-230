"""
A module for interfacing with projects.
"""

# built-in
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple, Optional

# internal
from userfs.build import build
from userfs.config import (
    Config,
    Interact,
    ProjectInteraction,
    ProjectSpecification,
)
from userfs.deploy import deploy
from userfs.fetch import fetch
from userfs.hooks import get_hooks
from userfs.update import update


class ProjectInteractionTask(NamedTuple):
    """
    A data structure containing all information necessary for interacting with
    a project.
    """

    kind: ProjectInteraction
    root: Path
    project: ProjectSpecification
    cli_options: Dict[str, Any]
    hooks: Dict[str, Optional[Interact]]
    hooks_only: bool = False

    def interact(self, interaction: Interact = None) -> None:
        """Run a project-interaction method."""

        self.project.logger.info("Starting '%s'.", self.kind.value)

        interactions = [self.hooks.get("pre")]
        if not self.hooks_only:
            interactions.append(interaction)
        interactions.append(self.hooks.get("post"))

        for inter in interactions:
            if inter is not None:
                inter(
                    self.root,
                    self.project,
                    self.project.options[self.kind],
                    self.cli_options,
                )

        self.project.logger.info("Finished '%s'.", self.kind.value)


INTERACTIONS = {
    ProjectInteraction.FETCH: fetch,
    ProjectInteraction.UPDATE: update,
    ProjectInteraction.BUILD: build,
    ProjectInteraction.DEPLOY: deploy,
}


def interact(task: ProjectInteractionTask) -> None:
    """Perform a project interaction."""
    task.interact(INTERACTIONS.get(task.kind))


def execute_interactions(
    interactions: Iterable[ProjectInteraction],
    projects: Iterable[str],
    config: Config,
    cli_options: Dict[str, Any],
    hooks_only: bool = False,
) -> int:
    """Execute project interactions in parallel."""

    hook_names = {"pre", "post"}

    for interaction in interactions:
        with Pool() as pool:
            pool.map(
                interact,
                [
                    ProjectInteractionTask(
                        interaction,
                        config.directory,
                        config.projects[x],
                        cli_options,
                        hooks=get_hooks(hook_names, x, interaction),
                        hooks_only=hooks_only,
                    )
                    for x in projects
                ],
            )
            pool.close()
            pool.join()

    return 0
