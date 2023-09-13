"""
A module implementing a configuration interface for the package.
"""

# built-in
from os.path import expandvars
from pathlib import Path
from typing import Any, Callable, Dict, List, cast

# third-party
from rcmpy.xdg import user_config
from vcorelib.dict import merge
from vcorelib.dict.codec import BasicDictCodec as _BasicDictCodec
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike, find_file, normalize

# internal
from userfs import PKG_NAME
from userfs.config.project import ProjectInteraction, ProjectSpecification
from userfs.config.source import SourceKind, SourceSpecification
from userfs.schemas import UserfsDictCodec as _UserfsDictCodec

#
# def interaction(
#     root: Path,
#     project: ProjectSpecification,
#     interaction_options: Dict[str, Any],
#     cli_options: Dict[str, Any],
# ) -> None:
#     """Project interaction."""
#
Interact = Callable[
    [Path, ProjectSpecification, Dict[str, Any], Dict[str, Any]], None
]

__all__ = [
    "ProjectInteraction",
    "ProjectSpecification",
    "SourceSpecification",
    "Config",
    "load_config",
    "SourceKind",
    "Interact",
]


class Config(_UserfsDictCodec, _BasicDictCodec):
    """The top-level configuration object for the package."""

    def init(self, data: _JsonObject) -> None:
        """Initialize this instance."""
        self.data = data

        # Directory where all actions should be carried out.
        self.directory: Path = Path(
            expandvars(str(data["directory"]))
        ).expanduser()

        # Paths to search for hooks.
        self.hook_paths: List[Path] = [self.directory.joinpath("hooks")]
        self.hook_paths.extend(
            Path(expandvars(x)).expanduser()  # type: ignore
            for x in data.get("hooks", [])  # type: ignore
        )

        # Load sources.
        self.sources: Dict[str, SourceSpecification] = {}
        for key, source_data in cast(
            Dict[str, Any], self.data.get("sources", {})
        ).items():
            self.sources[key] = SourceSpecification.from_json(source_data)

        # Load projects.
        self.projects: Dict[str, ProjectSpecification] = {}
        for key, project_data in cast(
            Dict[str, Any], self.data.get("projects", {})
        ).items():
            source_key: str = project_data["source"]
            assert source_key in self.sources, f"No source '{source_key}'!"
            self.projects[key] = ProjectSpecification.from_json(
                project_data, self.sources[source_key], key
            )


def load_config(root: Pathlike = None, name: str = "config.yaml") -> Config:
    """
    Load this package's configuration as a managed context. If changed at
    runtime, changes will be written back to disk.
    """

    if root is None:
        root = user_config(PKG_NAME)

    src_config = find_file("config.yaml", package=PKG_NAME)
    assert src_config is not None

    return Config.create(
        merge(
            _ARBITER.decode(
                src_config, includes_key="includes", require_success=True
            ).data,
            _ARBITER.decode(
                normalize(root, name), includes_key="includes"
            ).data,
        )
    )
