"""Reusable validation predicates."""

from __future__ import annotations

import re

from ..exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_email(value: str) -> bool:
    """Return True if the value looks like an email address."""

    return bool(_EMAIL_RE.match(value))


def require_non_empty(field: str, value: str) -> str:
    """Return the value or raise ValidationError if empty."""

    if not value or not value.strip():
        raise ValidationError(field, "must not be empty")
    return value
