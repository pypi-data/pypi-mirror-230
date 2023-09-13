"""
A module implementing a data structure for project sources.
"""

# built-in
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, cast

# third-party
from vcorelib.io import JsonObject


class SourceKind(Enum):
    """An enumeration describing kinds of sources."""

    GIT = "git"
    SRC = "src"


@dataclass
class SourceSpecification:
    """Informaiton describing a source specification."""

    kind: SourceKind
    suffix: str
    protocol: str
    user: str
    port: Optional[int]
    host: str
    attributes: Dict[str, Any]

    @staticmethod
    def from_json(data: JsonObject) -> "SourceSpecification":
        """Create a source specification from JSON data."""

        return SourceSpecification(
            SourceKind(data["kind"]),
            cast(str, data["suffix"]),
            cast(str, data["protocol"]),
            cast(str, data["user"]),
            cast(int, data.get("port")),
            cast(str, data["host"]),
            cast(Dict[str, Any], data.get("attributes", {})),
        )
