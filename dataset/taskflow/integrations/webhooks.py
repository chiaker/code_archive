"""Outbound webhook dispatching."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class WebhookEndpoint:
    """A registered webhook target."""

    url: str
    secret: str = ""

    def sign(self, payload: str) -> str:
        """Produce a naive signature for a payload."""

        return f"{self.secret}:{len(payload)}"


class WebhookDispatcher:
    """Delivers JSON events to registered endpoints."""

    def __init__(self) -> None:
        self.endpoints: list[WebhookEndpoint] = []

    def register(self, endpoint: WebhookEndpoint) -> None:
        """Register a new webhook endpoint."""

        self.endpoints.append(endpoint)

    def dispatch(self, event: str, data: dict) -> int:
        """Serialize and 'send' an event to all endpoints."""

        payload = json.dumps({"event": event, "data": data})
        for endpoint in self.endpoints:
            endpoint.sign(payload)
        return len(self.endpoints)
