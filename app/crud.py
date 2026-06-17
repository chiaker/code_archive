"""Database queries shared by the API endpoints.

Functions here are intentionally small and side-effect free so they can be
reused both by FastAPI endpoints and by tests.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .models import Definition, File


def list_files(
    db: Session,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Tuple[File, int]]:
    """Return every file together with how many functions it contains.

    Uses an outer join so files without any functions still appear with a
    count of ``0``. ``limit``/``offset`` paginate the result; ``limit=None``
    returns every file.
    """

    function_count = func.count(Definition.id).filter(Definition.kind == "function")
    stmt = (
        select(File, function_count)
        .outerjoin(Definition, Definition.file_id == File.id)
        .group_by(File.id)
        .order_by(File.name)
    )
    if offset:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    return [(file, count) for file, count in db.execute(stmt).all()]


def count_files(db: Session) -> int:
    """Return the total number of indexed files."""

    return db.execute(select(func.count(File.id))).scalar_one()


def get_stats(db: Session) -> dict:
    """Return summary counts: total files, functions and classes."""

    files_total = db.execute(select(func.count(File.id))).scalar_one()
    kind_counts = dict(
        db.execute(
            select(Definition.kind, func.count(Definition.id)).group_by(Definition.kind)
        ).all()
    )
    return {
        "files": files_total,
        "functions": kind_counts.get("function", 0),
        "classes": kind_counts.get("class", 0),
        "definitions": sum(kind_counts.values()),
    }


def get_file_structure(db: Session, name: str) -> Optional[File]:
    """Return a file (with its definitions loaded) by name, or ``None``."""

    stmt = (
        select(File)
        .options(selectinload(File.definitions))
        .where(File.name == name)
    )
    return db.execute(stmt).scalar_one_or_none()


def search_definitions(
    db: Session,
    q: str,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Definition]:
    """Return definitions whose name or docstring contains ``q``.

    Matching is case-insensitive (via ``lower``) and uses ``LIKE`` — for the
    expected dataset size this is simpler and sufficient compared to FTS.
    ``kind`` optionally narrows results to ``'function'`` or ``'class'``;
    ``limit``/``offset`` paginate the result.
    """

    pattern = f"%{q.lower()}%"
    name_match = func.lower(Definition.name).like(pattern)
    docstring_match = func.lower(Definition.docstring).like(pattern)
    stmt = (
        select(Definition)
        .options(selectinload(Definition.file))
        .where(name_match | docstring_match)
        .order_by(Definition.name)
    )
    if kind is not None:
        stmt = stmt.where(Definition.kind == kind)
    if offset:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())
