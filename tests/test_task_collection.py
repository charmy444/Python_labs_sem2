import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.domain.task import Task, TaskCollection


def test_task_collection_creation():
    collection = TaskCollection()

    assert len(collection) == 0
    assert collection.tasks == []


def test_task_collection_add():
    collection = TaskCollection()
    task = Task("task-1", {"action": "import"})

    collection.add(task)

    assert len(collection) == 1
    assert collection[0] == task


def test_task_collection_iter():
    collection = TaskCollection()
    task1 = Task("task-1", {"action": "import"})
    task2 = Task("task-2", {"action": "process"})

    collection.add(task1)
    collection.add(task2)

    assert list(collection) == [task1, task2]
