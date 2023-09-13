"""
A module for working with the Python search path.
"""

# built-in
from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Iterator, List


@contextmanager
def paths_added(paths: List[Path]) -> Iterator[None]:
    """Add search paths to sys.path as a context manager."""

    added = set()
    orig_set = set(sys.path)

    # Add provided paths.
    for path in [str(x) for x in paths]:
        if path not in orig_set and path not in added:
            sys.path.append(path)
            added.add(path)

    try:
        yield
    finally:
        # Remove paths that we actually added. Don't restore the previous state
        # of sys.path in case anything else modified it.
        restore_path = []
        for path in sys.path:
            if path not in added:
                restore_path.append(path)
        sys.path = restore_path
