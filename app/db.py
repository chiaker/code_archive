"""Database helpers for the code archive."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all ORM models."""


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "code_index.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"


def normalize_database_url(database_url_or_path: Optional[str] = None) -> str:
    """Return a SQLAlchemy database URL.

    Accepts either a full SQLAlchemy URL or a filesystem path to a SQLite file.
    """

    if database_url_or_path is None:
        env_value = os.getenv("ARCHIVE_DATABASE_URL")
        if env_value:
            return env_value
        return DEFAULT_DATABASE_URL

    value = str(database_url_or_path)
    if "://" in value:
        return value

    db_path = Path(value)
    if not db_path.is_absolute():
        db_path = (BASE_DIR / db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


def create_engine_for(database_url_or_path: Optional[str] = None) -> Engine:
    """Create a SQLAlchemy engine with SQLite-safe defaults."""

    database_url = normalize_database_url(database_url_or_path)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


engine = create_engine_for()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_session_factory(database_url_or_path: Optional[str] = None) -> Tuple[Engine, sessionmaker]:
    """Build an isolated engine/session factory pair.

    Useful for tests or CLI runs that should target a custom SQLite file.
    """

    custom_engine = create_engine_for(database_url_or_path)
    custom_session_local = sessionmaker(
        bind=custom_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return custom_engine, custom_session_local


def init_db(bind: Optional[Engine] = None) -> None:
    """Create database tables if they do not exist yet."""

    from . import models  # noqa: F401  # Ensure ORM classes are registered.

    Base.metadata.create_all(bind=bind or engine)


def get_db() -> Iterator[Session]:
    """Yield a database session for dependency injection."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
