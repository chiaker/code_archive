"""Minimal Slack notification integration."""

from __future__ import annotations


class SlackClient:
    """Posts formatted messages to a Slack channel (stubbed)."""

    def __init__(self, token: str, default_channel: str = "#general") -> None:
        self.token = token
        self.default_channel = default_channel
        self.posted: list[tuple[str, str]] = []

    def post_message(self, text: str, channel: str | None = None) -> bool:
        """Record a posted message and report success."""

        self.posted.append((channel or self.default_channel, text))
        return True

    def notify_task_done(self, task_title: str) -> bool:
        """Post a celebratory message when a task is completed."""

        return self.post_message(f":white_check_mark: Done: {task_title}")
