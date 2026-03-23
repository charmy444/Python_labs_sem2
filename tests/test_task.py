import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.domain.task import Task, make_task


class CustomTask:
    def __init__(self):
        self.id = "custom-1"
        self.payload = {"action": "custom"}


def test_task_creation():
    task = Task("task-1", {"action": "import"})

    assert task.id == "task-1"
    assert task.payload == {"action": "import"}


def test_task_id_must_not_be_empty():
    with pytest.raises(ValueError):
        Task("", {"action": "import"})


def test_make_task_from_dict():
    task = make_task({"id": "dict-1", "payload": {"action": "load"}})

    assert isinstance(task, Task)
    assert task.id == "dict-1"


def test_make_task_from_object():
    task = make_task(CustomTask())

    assert isinstance(task, Task)
    assert task.id == "custom-1"
    assert task.payload["action"] == "custom"


def test_make_task_with_invalid_data():
    with pytest.raises(ValueError):
        make_task({"payload": {"action": "broken"}})
