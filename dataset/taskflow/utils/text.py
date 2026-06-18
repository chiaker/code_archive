"""Text manipulation helpers."""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Convert arbitrary text into a lowercase hyphen slug."""

    return _SLUG_RE.sub("-", value.lower()).strip("-")


def truncate(value: str, length: int = 50, suffix: str = "…") -> str:
    """Truncate a string to a maximum length, adding a suffix."""

    if len(value) <= length:
        return value
    return value[: length - len(suffix)] + suffix


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
