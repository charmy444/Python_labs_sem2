import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.domain.task import (
    Task,
    TaskStateError,
    TaskTransitionError,
    TaskValidationError,
    make_task,
)


class CustomTask:
    def __init__(self):
        self.id = "custom-1"
        self.payload = {"action": "custom"}
        self.description = "Пользовательская задача"
        self.priority = 4


def test_task_creation():
    task = Task(
        "task-1",
        {"action": "import"},
        description="Импортировать данные",
        priority=2,
    )

    assert task.id == "task-1"
    assert task.payload == {"action": "import"}
    assert task.description == "Импортировать данные"
    assert task.priority == 2
    assert task.status == "pending"
    assert task.is_ready is True


def test_task_id_must_not_be_empty():
    with pytest.raises(TaskValidationError):
        Task("", {"action": "import"})


def test_make_task_from_dict():
    task = make_task(
        {
            "id": "dict-1",
            "payload": {"action": "load"},
            "description": "Загрузить данные",
            "priority": 5,
            "status": "pending",
            "created_at": "2026-04-12T10:30:00+03:00",
        }
    )

    assert isinstance(task, Task)
    assert task.id == "dict-1"
    assert task.description == "Загрузить данные"
    assert task.priority == 5
    assert task.created_at == datetime.fromisoformat("2026-04-12T10:30:00+03:00")


def test_make_task_from_object():
    task = make_task(CustomTask())

    assert isinstance(task, Task)
    assert task.id == "custom-1"
    assert task.payload["action"] == "custom"
    assert task.description == "Пользовательская задача"
    assert task.priority == 4


def test_make_task_with_invalid_data():
    with pytest.raises(TaskValidationError):
        make_task({"payload": {"action": "broken"}})


def test_priority_descriptor_validates_range():
    with pytest.raises(TaskValidationError):
        Task(
            "task-1",
            {"action": "import"},
            description="Импортировать данные",
            priority=8,
        )


def test_created_at_is_read_only_property():
    task = Task(
        "task-1",
        {"action": "import"},
        description="Импортировать данные",
    )

    with pytest.raises(AttributeError):
        task.created_at = datetime.now()


def test_task_cannot_start_without_description():
    task = Task("task-1", {"action": "import"})

    with pytest.raises(TaskStateError):
        task.start()


def test_task_allows_valid_status_transitions():
    task = Task(
        "task-1",
        {"action": "import"},
        description="Импортировать данные",
    )

    task.start()
    task.block()
    task.start()
    task.complete()

    assert task.status == "completed"
    assert task.is_ready is False


def test_task_rejects_invalid_status_transition():
    task = Task(
        "task-1",
        {"action": "import"},
        description="Импортировать данные",
    )

    task.start()
    task.complete()

    with pytest.raises(TaskTransitionError):
        task.status = "pending"


def test_non_data_descriptor_can_be_shadowed():
    task = Task(
        "task-1",
        {"action": "import"},
        description="Импортировать данные",
    )

    generated_summary = task.summary
    task.summary = "Локально переопределенное значение"

    assert generated_summary.startswith("task-1 [pending]")
    assert task.summary == "Локально переопределенное значение"
