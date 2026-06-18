"""Notification domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notification:
    """An in-app notification addressed to a user."""

    id: int
    user_id: int
    message: str
    created_at: datetime
    read: bool = False

    def mark_read(self) -> None:
        """Mark the notification as read."""

        self.read = True


def unread_count(notifications: list[Notification]) -> int:
    """Count unread notifications in a list."""

    return sum(1 for n in notifications if not n.read)
