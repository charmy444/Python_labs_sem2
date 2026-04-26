import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.domain.task import Task, TaskCollection, TaskQueue, TaskValidationError


def make_ready_task(task_id: str, priority: int = 3, status: str = "pending") -> Task:
    return Task(
        task_id,
        {"action": f"process-{task_id}"},
        description=f"Задача {task_id}",
        priority=priority,
        status=status,
    )


def test_task_queue_creation():
    queue = TaskQueue()

    assert len(queue) == 0
    assert queue.tasks == []
    assert TaskCollection is TaskQueue


def test_task_queue_add():
    queue = TaskQueue()
    task = make_ready_task("task-1")

    queue.add(task)

    assert len(queue) == 1
    assert queue[0] == task


def test_task_queue_supports_repeated_iteration():
    task1 = make_ready_task("task-1", priority=2)
    task2 = make_ready_task("task-2", priority=5)
    queue = TaskQueue([task1, task2])

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == ["task-1", "task-2"]
    assert second_pass == first_pass
    assert sum(task.priority for task in queue) == 7


def test_task_queue_iterator_raises_stop_iteration():
    queue = TaskQueue([make_ready_task("task-1")])
    iterator = iter(queue)

    assert next(iterator).id == "task-1"

    with pytest.raises(StopIteration):
        next(iterator)


def test_task_queue_filters_by_status_lazily():
    task = make_ready_task("task-1")
    queue = TaskQueue([task])
    completed_tasks = queue.filter_by_status("completed")

    task.start()
    task.complete()

    assert [item.id for item in completed_tasks] == ["task-1"]


def test_task_queue_filters_by_priority():
    queue = TaskQueue(
        [
            make_ready_task("task-1", priority=1),
            make_ready_task("task-2", priority=4),
            make_ready_task("task-3", priority=4),
        ]
    )

    assert [task.id for task in queue.filter_by_priority(4)] == ["task-2", "task-3"]


def test_task_queue_rejects_invalid_filter_values():
    queue = TaskQueue([make_ready_task("task-1")])

    with pytest.raises(TaskValidationError):
        list(queue.filter_by_status("unknown"))

    with pytest.raises(TaskValidationError):
        list(queue.filter_by_priority(10))


def test_task_queue_rejects_non_task_items():
    queue = TaskQueue()

    with pytest.raises(TypeError):
        queue.add({"id": "not-a-task"})  # type: ignore[arg-type]
