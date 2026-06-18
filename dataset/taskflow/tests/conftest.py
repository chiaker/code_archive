"""Shared test fixtures."""

from __future__ import annotations

from ..repositories.task_repo import TaskRepository
from ..repositories.user_repo import UserRepository


def make_task_repo() -> TaskRepository:
    """Return an empty task repository for tests."""

    return TaskRepository()


def make_user_repo() -> UserRepository:
    """Return an empty user repository for tests."""

    return UserRepository()
