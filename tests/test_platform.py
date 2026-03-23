import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.app.platform import TaskPlatform
from src.domain.task import TaskCollection
from src.source.api_source import ApiTaskSource
from src.source.file_source import FileTaskSource
from src.source.generator_source import GeneratorTaskSource


class WrongSource:
    pass


def test_platform_creation():
    platform = TaskPlatform()

    assert platform.sources == []
    assert isinstance(platform.task_collection, TaskCollection)
    assert len(platform.task_collection) == 0


def test_platform_add_wrong_source():
    platform = TaskPlatform()

    with pytest.raises(TypeError):
        platform.add_source(WrongSource())


def test_platform_receive_tasks_from_different_sources(tmp_path):
    file_path = tmp_path / "tasks.json"
    file_path.write_text(
        json.dumps([{"id": "file-1", "payload": {"action": "load"}}]),
        encoding="utf-8",
    )

    platform = TaskPlatform()
    platform.add_source(FileTaskSource(file_path))
    platform.add_source(
        GeneratorTaskSource(lambda: [{"id": "generator-1", "payload": {"action": "build"}}])
    )
    platform.add_source(
        ApiTaskSource([{"id": "api-1", "payload": {"action": "notify"}}], "mock-api")
    )

    tasks = platform.receive_tasks()

    assert len(tasks) == 3
    assert tasks[0].id == "file-1"
    assert tasks[1].id == "generator-1"
    assert tasks[2].id == "api-1"
