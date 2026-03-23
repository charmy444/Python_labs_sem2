from src.contacts.task_source import TaskSource
from src.domain.task import TaskCollection


class TaskPlatform:
    def __init__(self) -> None:
        self.sources: list[TaskSource] = []
        self.task_collection = TaskCollection()

    def add_source(self, source: object) -> None:
        if not isinstance(source, TaskSource):
            raise TypeError("Источник должен реализовать метод get_tasks")
        self.sources.append(source)

    def receive_tasks(self) -> TaskCollection:
        self.task_collection = TaskCollection()
        for source in self.sources:
            for task in source.get_tasks():
                self.task_collection.add(task)
        return self.task_collection
