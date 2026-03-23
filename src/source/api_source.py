from collections.abc import Iterable

from src.domain.task import Task, make_task


class ApiTaskSource:
    def __init__(self, tasks: Iterable[object], endpoint_name: str = "mock-api"):
        self.tasks = list(tasks)
        self.endpoint_name = endpoint_name

    def get_tasks(self) -> list[Task]:
        return [make_task(item) for item in self.tasks]
