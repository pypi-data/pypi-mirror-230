"""
A module implementing a data structure describing projects.
"""

# built-in
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, cast

# third-party
from vcorelib.io import JsonObject
from vcorelib.logging import LoggerType
from vcorelib.paths import Pathlike, normalize

# internal
from userfs.config.source import SourceSpecification


class ProjectInteraction(Enum):
    """Kinds of project interactions."""

    FETCH = "fetch"
    UPDATE = "update"
    BUILD = "build"
    DEPLOY = "deploy"
    CUSTOM = "custom"


@dataclass
class ProjectSpecification:
    """Information describing a software project and how to obtain it."""

    source: SourceSpecification
    logger: LoggerType

    path: str
    repository: str
    attributes: Dict[str, Any]
    options: Dict[ProjectInteraction, Dict[str, Any]]

    @property
    def url(self) -> str:
        """Get a URL to this project's source."""

        source = self.source
        proto = source.protocol
        result = f"{source.protocol}://"

        if proto == "ssh":
            result += source.user + "@"

        result += source.host

        if source.port is not None:
            result += ":" + str(source.port)

        return result + "/" + self.path + "/" + self.repository + source.suffix

    def location(self, root: Pathlike = None) -> Path:
        """Get a disk location for this project."""

        # Only allow one layer of depths.
        subdir = Path(self.path).name
        return normalize(root).joinpath(subdir, self.repository)

    @staticmethod
    def from_json(
        data: JsonObject, source: SourceSpecification, key: str
    ) -> "ProjectSpecification":
        """Create a project specification from JSON data."""

        path = cast(str, data["path"])
        repo = cast(str, data.get("repository", key))

        return ProjectSpecification(
            source,
            getLogger(Path(path).name + "/" + repo),
            path,
            repo,
            cast(Dict[str, Any], data.get("attributes", {})),
            {
                kind: cast(Dict[str, Any], data.get(kind.value, {}))
                for kind in ProjectInteraction
            },
        )
