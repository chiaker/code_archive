"""Command-line entry point for TaskFlow administration."""

from __future__ import annotations

import argparse

from .logging_setup import configure_logging
from .repositories.project_repo import ProjectRepository
from .services.project_service import ProjectService


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""

    parser = argparse.ArgumentParser(prog="taskflow", description="TaskFlow admin CLI")
    sub = parser.add_subparsers(dest="command")

    create = sub.add_parser("create-project", help="Create a new project")
    create.add_argument("name")
    create.add_argument("--owner", type=int, default=1)
    return parser


def run(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch the requested command."""

    configure_logging()
    args = build_parser().parse_args(argv)

    if args.command == "create-project":
        service = ProjectService(ProjectRepository())
        project = service.create(args.name, args.owner)
        print(f"Created project {project.slug!r} (id={project.id})")
        return 0

    print("No command given. Use --help.")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
