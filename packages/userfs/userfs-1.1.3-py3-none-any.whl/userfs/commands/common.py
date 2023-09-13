"""
Common argument-parsing utilities for package commands.
"""
# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path as _Path
from re import search
from typing import Any, Dict, Iterable, Set, Tuple

# internal
from userfs.config import Config, ProjectInteraction, load_config
from userfs.paths import paths_added
from userfs.project import execute_interactions


def add_common(parser: _ArgumentParser, projects: bool = True) -> None:
    """Add common command options."""

    parser.add_argument(
        "-c",
        "--config",
        type=_Path,
        help="an optional path to the configuration directory",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="interact with all configured projects",
    )
    parser.add_argument(
        "-n",
        "--no-interact",
        action="store_true",
        help="don't run package-implemented interactions",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default=".*",
        help=(
            "a pattern to use to select project "
            "specifications filtered by name"
        ),
    )

    if projects:
        parser.add_argument(
            "projects",
            nargs="*",
            help=(
                "specific projects to build, arguments in the "
                "form 'key=value' will be provided as interaction options"
            ),
        )


def get_projects(
    args: _Namespace, config: Config
) -> Tuple[Set[str], Dict[str, Any]]:
    """Get a set of projects based on command-line arguments."""

    # Parse options.
    opts = {}
    for opt in set(x for x in args.projects if "=" in x):
        split = opt.split("=", maxsplit=1)
        opts[split[0]] = split[1]

    # Apply filter.
    return (
        set(
            filter(
                lambda x: search(args.pattern, x) and x in config.projects,
                # Gather the set of projects.
                set(x for x in args.projects if "=" not in x)
                if not args.all
                else set(config.projects.keys()),
            )
        ),
        opts,
    )


def run_command(
    interactions: Iterable[ProjectInteraction], args: _Namespace
) -> int:
    """Run a project interaction command."""

    config = load_config(root=args.config)

    projects, options = get_projects(args, config)

    with paths_added(config.hook_paths):
        return execute_interactions(
            interactions,
            projects,
            config,
            options,
            hooks_only=args.no_interact,
        )
