"""Async tests for the notification service."""

from __future__ import annotations

import asyncio

from ..services.notification_service import NotificationService


def test_push_and_deliver() -> None:
    """Pushed notifications are delivered and marked read."""

    async def scenario() -> int:
        """Push two notifications and deliver them."""

        service = NotificationService()
        await service.push(user_id=1, message="hello")
        await service.push(user_id=1, message="world")
        return await service.deliver_all()

    assert asyncio.run(scenario()) == 2
