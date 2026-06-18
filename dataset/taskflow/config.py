"""Application configuration loading and access."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Runtime settings assembled from environment variables."""

    database_url: str = "sqlite:///taskflow.db"
    secret_key: str = "dev-secret"
    debug: bool = False
    page_size: int = 25
    allowed_hosts: list[str] = field(default_factory=lambda: ["localhost"])

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from the process environment."""

        return cls(
            database_url=os.getenv("TASKFLOW_DB", cls.database_url),
            secret_key=os.getenv("TASKFLOW_SECRET", cls.secret_key),
            debug=os.getenv("TASKFLOW_DEBUG", "0") == "1",
            page_size=int(os.getenv("TASKFLOW_PAGE_SIZE", str(cls.page_size))),
        )

    @property
    def is_sqlite(self) -> bool:
        """Whether the configured database is SQLite."""

        return self.database_url.startswith("sqlite")


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance, loading it on first call."""

    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
