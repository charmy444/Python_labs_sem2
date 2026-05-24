from src.app.executor import AsyncExecutor
from src.contacts.task_source import TaskSource
from src.domain.task import TaskQueue


class TaskPlatform:
    def __init__(self) -> None:
        self.sources: list[TaskSource] = []
        self.task_queue = TaskQueue()
        self.task_collection = self.task_queue
        self.executor = AsyncExecutor()

    def add_source(self, source: object) -> None:
        if not isinstance(source, TaskSource):
            raise TypeError("Источник должен реализовать метод get_tasks")
        self.sources.append(source)

    def receive_tasks(self) -> TaskQueue:
        self.task_queue = TaskQueue()
        self.task_collection = self.task_queue
        for source in self.sources:
            for task in source.get_tasks():
                self.task_queue.add(task)
        return self.task_queue

    async def run_async(self) -> None:
        """Асинхронный запуск платформы."""
        self.receive_tasks()
        async with self.executor as executor:
            for task in self.task_queue:
                await executor.submit(task)
            # Контекстный менеджер сам подождет завершения всех задач
