"""Shared pytest fixtures: an isolated SQLite DB and a TestClient.

Each test gets its own temporary SQLite file so tests never touch the real
``code_index.db``. The FastAPI ``get_db`` dependency is overridden to hand out
sessions bound to that temporary database.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import create_session_factory, get_db, init_db
from app.main import app
from app.models import Definition, File

# Directory with the tiny sample project used by the indexer tests.
SAMPLE_CODE = Path(__file__).parent / "sample_code"


@pytest.fixture
def session_factory(tmp_path):
    """Build a session factory bound to a fresh per-test SQLite file."""

    engine, SessionLocal = create_session_factory(str(tmp_path / "test.db"))
    init_db(bind=engine)
    return SessionLocal


@pytest.fixture
def client(session_factory):
    """A TestClient whose ``get_db`` uses the per-test database.

    The client is created without the ``with`` block on purpose so the app
    lifespan (which would call ``init_db()`` on the real engine) does not run.
    """

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def seeded(session_factory):
    """Insert deterministic data and return the same session factory.

    ``auth.py`` has one class + two functions; ``empty.py`` has no
    definitions (so it exercises the "zero functions" / empty-structure paths).
    """

    with session_factory() as db:
        auth = File(name="auth.py", path="src/auth.py")
        auth.definitions = [
            Definition(
                name="TokenService",
                kind="class",
                line_start=4,
                line_end=14,
                docstring="Issue and validate tokens.",
            ),
            Definition(
                name="issue",
                kind="function",
                line_start=7,
                line_end=14,
                docstring="Create a token for a user.",
            ),
            Definition(
                name="hash_password",
                kind="function",
                line_start=17,
                line_end=20,
                docstring="Hash a password.",
            ),
        ]
        empty = File(name="empty.py", path="src/empty.py")
        db.add_all([auth, empty])
        db.commit()

    return session_factory
