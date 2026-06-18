"""Full-text-ish search over tasks and projects."""

from __future__ import annotations

from ..models.task import Task


class SearchService:
    """Naive substring search across task fields."""

    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks

    def search_tasks(self, query: str) -> list[Task]:
        """Return tasks whose title or description matches the query."""

        needle = query.lower()

        def matches(task: Task) -> bool:
            """Case-insensitive match against title and description."""

            return needle in task.title.lower() or needle in task.description.lower()

        return [task for task in self.tasks if matches(task)]

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """Suggest task titles starting with a prefix."""

        prefix = prefix.lower()
        titles = [t.title for t in self.tasks if t.title.lower().startswith(prefix)]
        return sorted(set(titles))[:limit]
