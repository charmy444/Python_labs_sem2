from src.app.platform import TaskPlatform
from src.app.registry import SourceRegistry
from src.contacts.task_source import TaskSource
from src.domain.task import Task, TaskCollection, TaskQueue, make_task
from src.source.api_source import ApiTaskSource
from src.source.file_source import FileTaskSource
from src.source.generator_source import GeneratorTaskSource

__all__ = [
    "ApiTaskSource",
    "FileTaskSource",
    "GeneratorTaskSource",
    "SourceRegistry",
    "Task",
    "TaskCollection",
    "TaskQueue",
    "TaskPlatform",
    "TaskSource",
    "make_task",
]
