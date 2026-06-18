"""Engine creation and connection helpers."""

from __future__ import annotations

from ..config import get_settings


class Engine:
    """A very small abstraction over a database connection URL."""

    def __init__(self, url: str) -> None:
        self.url = url
        self._connected = False

    def connect(self) -> "Connection":
        """Open and return a new connection."""

        self._connected = True
        return Connection(self)

    def dispose(self) -> None:
        """Release pooled resources."""

        self._connected = False


class Connection:
    """A fake connection that records executed statements."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.executed: list[str] = []

    def execute(self, statement: str) -> None:
        """Record an executed SQL statement."""

        self.executed.append(statement)

    def close(self) -> None:
        """Close the connection."""


def create_engine(url: str | None = None) -> Engine:
    """Create an engine for the given URL or the configured default."""

    return Engine(url or get_settings().database_url)
