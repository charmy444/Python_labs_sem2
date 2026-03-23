import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.domain.task import Task
from src.source.api_source import ApiTaskSource
from src.source.file_source import FileTaskSource
from src.source.generator_source import GeneratorTaskSource


class ApiTaskObject:
    def __init__(self):
        self.id = "api-1"
        self.payload = {"action": "notify"}


def test_file_task_source(tmp_path):
    file_path = tmp_path / "tasks.json"
    file_path.write_text(
        json.dumps(
            [
                {"id": "file-1", "payload": {"action": "load"}},
                {"id": "file-2", "payload": {"action": "archive"}},
            ]
        ),
        encoding="utf-8",
    )

    source = FileTaskSource(file_path)
    tasks = source.get_tasks()

    assert len(tasks) == 2
    assert isinstance(tasks[0], Task)
    assert tasks[0].id == "file-1"


def test_generator_task_source():
    def generator_func():
        return [
            {"id": "generator-1", "payload": {"action": "first"}},
            {"id": "generator-2", "payload": {"action": "second"}},
        ]

    source = GeneratorTaskSource(generator_func)
    tasks = source.get_tasks()

    assert len(tasks) == 2
    assert tasks[1].id == "generator-2"


def test_api_task_source():
    source = ApiTaskSource([ApiTaskObject()], "orders-api")
    tasks = source.get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == "api-1"
    assert source.endpoint_name == "orders-api"


def test_file_task_source_with_invalid_json(tmp_path):
    file_path = tmp_path / "tasks.json"
    file_path.write_text("{broken json", encoding="utf-8")

    source = FileTaskSource(file_path)

    with pytest.raises(ValueError):
        source.get_tasks()
