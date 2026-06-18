"""Declarative base and shared mixins for ORM models."""

from __future__ import annotations

from datetime import datetime


class Base:
    """Minimal declarative base stand-in for the demo project."""

    id: int

    def to_dict(self) -> dict:
        """Return a plain-dict view of the model's public attributes."""

        return {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("_")
        }


class TimestampMixin:
    """Adds created/updated timestamps to a model."""

    created_at: datetime
    updated_at: datetime

    def touch(self) -> None:
        """Update the ``updated_at`` timestamp to now."""

        self.updated_at = datetime.utcnow()
