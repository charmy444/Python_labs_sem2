from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    id: str
    payload: Any

    def __post_init__(self) -> None:
        if not str(self.id).strip():
            raise ValueError("У задачи должен быть непустой id")
        self.id = str(self.id)


class TaskCollection:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def __getitem__(self, key: int | slice) -> Task | list[Task]:
        return self.tasks[key]

    def __iter__(self) -> Iterator[Task]:
        return iter(self.tasks)

    def __len__(self) -> int:
        return len(self.tasks)

    def add(self, task: Task) -> None:
        self.tasks.append(task)


def make_task(raw_task: object) -> Task:
    if isinstance(raw_task, Task):
        return raw_task

    if isinstance(raw_task, Mapping):
        if "id" not in raw_task or "payload" not in raw_task:
            raise ValueError("Словарь задачи должен содержать id и payload")
        return Task(raw_task["id"], raw_task["payload"])

    if hasattr(raw_task, "id") and hasattr(raw_task, "payload"):
        return Task(getattr(raw_task, "id"), getattr(raw_task, "payload"))

    raise ValueError("Неподходящий формат задачи")
