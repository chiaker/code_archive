"""Project-wide constants and enumerations."""

from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle states a task can be in."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Priority(int, Enum):
    """Numeric task priorities, higher is more urgent."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Role(str, Enum):
    """Roles a user can hold within a project."""

    VIEWER = "viewer"
    MEMBER = "member"
    ADMIN = "admin"


DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 200
SUPPORTED_LOCALES = ("en", "ru", "de")
