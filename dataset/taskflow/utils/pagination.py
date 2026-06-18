"""Pagination helpers shared by list endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

from ..constants import MAX_PAGE_SIZE

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """A single page of results plus metadata."""

    items: Sequence[T]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        """Whether more items exist after this page."""

        return self.offset + len(self.items) < self.total


def paginate(items: Sequence[T], limit: int, offset: int = 0) -> Page[T]:
    """Slice a sequence into a Page, clamping the limit."""

    limit = max(1, min(limit, MAX_PAGE_SIZE))
    window = items[offset : offset + limit]
    return Page(items=window, total=len(items), limit=limit, offset=offset)
