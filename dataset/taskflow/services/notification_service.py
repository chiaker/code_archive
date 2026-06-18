"""Asynchronous notification dispatching."""

from __future__ import annotations

import asyncio
from datetime import datetime

from ..models.notification import Notification


class NotificationService:
    """Queues and delivers notifications asynchronously."""

    def __init__(self) -> None:
        self._queue: list[Notification] = []
        self._seq = 0

    async def push(self, user_id: int, message: str) -> Notification:
        """Enqueue a notification for a user."""

        self._seq += 1
        note = Notification(id=self._seq, user_id=user_id, message=message, created_at=datetime.utcnow())
        self._queue.append(note)
        await asyncio.sleep(0)
        return note

    async def deliver_all(self) -> int:
        """Deliver every queued notification, returning the count."""

        delivered = 0
        while self._queue:
            note = self._queue.pop(0)
            await self._send(note)
            delivered += 1
        return delivered

    async def _send(self, note: Notification) -> None:
        """Pretend to send a single notification over the wire."""

        await asyncio.sleep(0)
        note.mark_read()
