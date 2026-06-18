"""Generic in-memory repository base class."""

from __future__ import annotations

from typing import Generic, Iterable, Optional, TypeVar

from ..exceptions import NotFoundError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """A minimal CRUD repository backed by a dict."""

    def __init__(self) -> None:
        self._items: dict[int, T] = {}
        self._next_id = 1

    def add(self, entity: T) -> T:
        """Store an entity, assigning an id if needed."""

        entity_id = getattr(entity, "id", None) or self._next_id
        setattr(entity, "id", entity_id)
        self._items[entity_id] = entity
        self._next_id = max(self._next_id, entity_id) + 1
        return entity

    def get(self, entity_id: int) -> Optional[T]:
        """Return an entity by id or None."""

        return self._items.get(entity_id)

    def get_or_raise(self, entity_id: int) -> T:
        """Return an entity by id or raise NotFoundError."""

        entity = self.get(entity_id)
        if entity is None:
            raise NotFoundError(f"{type(self).__name__}: id={entity_id}")
        return entity

    def list(self) -> list[T]:
        """Return all stored entities."""

        return list(self._items.values())

    def delete(self, entity_id: int) -> None:
        """Remove an entity by id, ignoring missing ones."""

        self._items.pop(entity_id, None)

    def filter(self, predicate) -> Iterable[T]:
        """Yield entities matching a predicate callable."""

        for item in self._items.values():
            if predicate(item):
                yield item
