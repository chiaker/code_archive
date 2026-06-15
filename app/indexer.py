"""Command-line indexer for Python source trees."""

from __future__ import annotations

import argparse
import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session

from .db import create_session_factory, init_db
from .models import Definition, File


LOGGER = logging.getLogger(__name__)


@dataclass
class DefinitionRecord:
    """Normalized information extracted from an AST node."""

    name: str
    kind: str
    line_start: int
    line_end: int
    docstring: Optional[str]


@dataclass
class FileRecord:
    """Parsed information about a single Python file."""

    name: str
    path: str
    definitions: list[DefinitionRecord]


def discover_python_files(root: Path) -> list[Path]:
    """Return all Python files under ``root`` in a stable order."""

    return sorted(path for path in root.rglob("*.py") if path.is_file())


def collect_definitions(tree: ast.AST) -> list[ast.AST]:
    """Collect function and class nodes from an AST tree."""

    allowed_nodes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    nodes = [node for node in ast.walk(tree) if isinstance(node, allowed_nodes)]
    nodes.sort(key=lambda node: (getattr(node, "lineno", 0), getattr(node, "col_offset", 0), node.name))
    return nodes


def extract_definitions(tree: ast.AST) -> list[DefinitionRecord]:
    """Convert AST nodes into serializable definition records."""

    records: list[DefinitionRecord] = []
    for node in collect_definitions(tree):
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        line_start = getattr(node, "lineno", 0)
        line_end = getattr(node, "end_lineno", None) or line_start
        records.append(
            DefinitionRecord(
                name=node.name,
                kind=kind,
                line_start=line_start,
                line_end=line_end,
                docstring=ast.get_docstring(node, clean=True),
            )
        )
    return records


def parse_file(path: Path, root: Path) -> Optional[FileRecord]:
    """Parse one Python file and return its structured representation."""

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        LOGGER.warning("Skipping %s: %s", path, exc)
        return None

    relative_path = path.relative_to(root).as_posix()
    return FileRecord(
        name=path.name,
        path=relative_path,
        definitions=extract_definitions(tree),
    )


def clear_tables(session: Session) -> None:
    """Remove all previously indexed rows before re-indexing."""

    session.execute(delete(Definition))
    session.execute(delete(File))
    session.commit()


def ensure_unique_file_name(candidate: str, relative_path: str, used_names: set[str]) -> str:
    """Return a stable unique file identifier for the database."""

    if candidate not in used_names:
        return candidate

    if relative_path not in used_names:
        LOGGER.warning("Duplicate file name %s detected; using %s instead", candidate, relative_path)
        return relative_path

    suffix = 2
    while f"{relative_path}#{suffix}" in used_names:
        suffix += 1

    unique_name = f"{relative_path}#{suffix}"
    LOGGER.warning("Duplicate file name %s detected; using %s instead", candidate, unique_name)
    return unique_name


def index_directory(source_root: Path, database_url_or_path: Optional[str] = None) -> int:
    """Index all Python files inside ``source_root`` into SQLite."""

    source_root = source_root.expanduser().resolve()
    if not source_root.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_root}")
    if not source_root.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_root}")

    engine, session_local = create_session_factory(database_url_or_path)
    init_db(bind=engine)

    python_files = discover_python_files(source_root)
    with session_local() as session:
        clear_tables(session)
        used_names: set[str] = set()

        indexed_files = 0
        for path in python_files:
            parsed = parse_file(path, source_root)
            if parsed is None:
                continue

            file_name = ensure_unique_file_name(parsed.name, parsed.path, used_names)
            used_names.add(file_name)

            file_row = File(name=file_name, path=parsed.path)
            for definition in parsed.definitions:
                file_row.definitions.append(
                    Definition(
                        name=definition.name,
                        kind=definition.kind,
                        line_start=definition.line_start,
                        line_end=definition.line_end,
                        docstring=definition.docstring,
                    )
                )
            session.add(file_row)
            indexed_files += 1

        session.commit()

    LOGGER.info("Indexed %s Python files from %s", indexed_files, source_root)
    return indexed_files


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(description="Index Python files into SQLite.")
    parser.add_argument("source", nargs="?", default="dataset", help="Directory with .py files")
    parser.add_argument(
        "--db",
        dest="database",
        default=None,
        help="SQLite file path or SQLAlchemy database URL",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO))
    indexed = index_directory(Path(args.source), database_url_or_path=args.database)
    print(f"Indexed {indexed} files into SQLite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
