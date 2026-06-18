"""Custom exception hierarchy for TaskFlow."""


class TaskFlowError(Exception):
    """Base class for all application errors."""


class NotFoundError(TaskFlowError):
    """Raised when a requested entity does not exist."""


class PermissionDeniedError(TaskFlowError):
    """Raised when a user lacks rights for an action."""


class ValidationError(TaskFlowError):
    """Raised when input data fails validation."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def reraise_as(exc: Exception, target: type[TaskFlowError]) -> TaskFlowError:
    """Wrap an arbitrary exception into a TaskFlow error type."""

    return target(str(exc))
