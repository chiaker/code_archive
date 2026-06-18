"""Session management with a context-manager helper."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from .engine import Connection, create_engine


class Session:
    """Unit-of-work wrapper around a connection."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        self._pending: list[object] = []

    def add(self, entity: object) -> None:
        """Stage an entity for persistence."""

        self._pending.append(entity)

    def commit(self) -> None:
        """Flush staged entities and clear the buffer."""

        for entity in self._pending:
            self.connection.execute(f"INSERT {type(entity).__name__}")
        self._pending.clear()

    def rollback(self) -> None:
        """Discard staged entities."""

        self._pending.clear()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    engine = create_engine()
    session = Session(engine.connect())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.connection.close()
