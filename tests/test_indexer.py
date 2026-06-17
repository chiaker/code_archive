"""Tests for the AST indexer (Stage A behaviour, re-verified here)."""

from __future__ import annotations

from sqlalchemy import select

from app.crud import get_stats
from app.db import create_session_factory
from app.indexer import index_directory
from app.models import Definition, File
from tests.conftest import SAMPLE_CODE


def _index_sample(tmp_path):
    """Index the sample project into a fresh DB and return its session factory."""

    db_file = str(tmp_path / "indexed.db")
    indexed = index_directory(SAMPLE_CODE, database_url_or_path=db_file)
    _, SessionLocal = create_session_factory(db_file)
    return indexed, SessionLocal


def test_broken_file_is_skipped_not_fatal(tmp_path):
    """bad_syntax.py must be skipped; only the two valid files are indexed."""

    indexed, SessionLocal = _index_sample(tmp_path)

    assert indexed == 2
    with SessionLocal() as db:
        assert db.execute(select(File)).scalars().all().__len__() == 2


def test_extracts_functions_classes_and_nested(tmp_path):
    """Top-level, nested, async functions and classes are all captured."""

    _, SessionLocal = _index_sample(tmp_path)

    with SessionLocal() as db:
        names = {
            d.name: d.kind
            for d in db.execute(select(Definition)).scalars().all()
        }

    # module_a.py: alpha, beta (async), Widget, render (method), helper (nested)
    assert names["alpha"] == "function"
    assert names["beta"] == "function"        # async def counts as a function
    assert names["Widget"] == "class"
    assert names["render"] == "function"      # method
    assert names["helper"] == "function"      # nested function
    assert names["gamma"] == "function"       # from pkg/module_a.py


def test_line_numbers_and_docstring(tmp_path):
    """Line span and docstring are extracted for a known definition."""

    _, SessionLocal = _index_sample(tmp_path)

    with SessionLocal() as db:
        alpha = db.execute(
            select(Definition).where(Definition.name == "alpha")
        ).scalar_one()

    assert alpha.line_start == 4
    assert alpha.line_end >= alpha.line_start
    assert alpha.docstring == "Return x unchanged."


def test_duplicate_basename_kept_unique(tmp_path):
    """Two files named module_a.py in different folders stay distinct."""

    _, SessionLocal = _index_sample(tmp_path)

    with SessionLocal() as db:
        files = db.execute(select(File)).scalars().all()
        names = [f.name for f in files]

    assert len(names) == len(set(names))  # names are unique
    assert any(f.name == "module_a.py" for f in files)


def test_reindex_is_idempotent(tmp_path):
    """Running the indexer twice does not duplicate rows."""

    db_file = str(tmp_path / "idem.db")
    first = index_directory(SAMPLE_CODE, database_url_or_path=db_file)
    second = index_directory(SAMPLE_CODE, database_url_or_path=db_file)

    assert first == second == 2
    _, SessionLocal = create_session_factory(db_file)
    with SessionLocal() as db:
        stats = get_stats(db)

    assert stats["files"] == 2
    assert stats["classes"] == 1  # only Widget
