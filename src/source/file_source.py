import json
from pathlib import Path

from src.domain.task import Task, make_task


class FileTaskSource:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def get_tasks(self) -> list[Task]:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("Файл содержит некорректный JSON") from error

        if not isinstance(data, list):
            raise ValueError("Файл должен содержать список задач")

        return [make_task(item) for item in data]
