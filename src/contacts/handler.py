from typing import Protocol, runtime_checkable

from src.domain.task import Task


@runtime_checkable
class TaskHandler(Protocol):
    """Протокол обработчика задачи."""

    async def handle(self, task: Task) -> None:
        """Обработать задачу асинхронно."""
        ...
