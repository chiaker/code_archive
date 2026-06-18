"""Asynchronous email-sending worker."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """A queued outbound email."""

    to: str
    subject: str
    body: str


class EmailWorker:
    """Consumes email messages from an async queue."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue[EmailMessage] = asyncio.Queue()
        self.sent = 0

    async def enqueue(self, message: EmailMessage) -> None:
        """Add a message to the outbound queue."""

        await self.queue.put(message)

    async def run(self, max_messages: int | None = None) -> int:
        """Process queued messages until empty or a cap is reached."""

        processed = 0
        while not self.queue.empty():
            message = await self.queue.get()
            await self._send(message)
            processed += 1
            if max_messages is not None and processed >= max_messages:
                break
        return processed

    async def _send(self, message: EmailMessage) -> None:
        """Simulate sending one email."""

        await asyncio.sleep(0)
        self.sent += 1
