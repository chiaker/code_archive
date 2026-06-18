"""Attachment domain model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Attachment:
    """A file attached to a task."""

    id: int
    task_id: int
    filename: str
    size_bytes: int
    content_type: str = "application/octet-stream"

    @property
    def human_size(self) -> str:
        """Human-readable file size."""

        size = float(self.size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def is_image(self) -> bool:
        """Whether the attachment is an image by content type."""

        return self.content_type.startswith("image/")
