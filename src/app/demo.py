from pathlib import Path

from src.app.platform import TaskPlatform
from src.app.registry import SourceRegistry
from src.contacts.task_source import TaskSource
from src.domain.task import TaskQueue
from src.source.api_source import ApiTaskSource
from src.source.file_source import FileTaskSource
from src.source.generator_source import GeneratorTaskSource


class ApiTaskData:
    def __init__(
        self,
        task_id: str,
        payload: dict[str, object],
        description: str,
        priority: int,
        status: str = "pending",
    ):
        self.id = task_id
        self.payload = payload
        self.description = description
        self.priority = priority
        self.status = status


def create_generated_tasks(count: int = 2) -> list[dict[str, object]]:
    tasks = []
    for number in range(1, count + 1):
        tasks.append(
            {
                "id": f"generator-{number}",
                "payload": {
                    "action": "generated_task",
                    "number": number,
                },
                "description": f"Сгенерированная задача №{number}",
                "priority": min(number + 1, 5),
                "status": "pending",
            }
        )
    return tasks


def create_api_tasks() -> list[ApiTaskData]:
    return [
        ApiTaskData(
            "api-1",
            {"action": "send_notification", "channel": "email"},
            "Отправить уведомление клиенту",
            4,
        ),
        ApiTaskData(
            "api-2",
            {"action": "process_order", "order_id": 1042},
            "Обработать заказ 1042",
            5,
            "in_progress",
        ),
    ]


def create_demo_platform(generated_count: int = 2) -> TaskPlatform:
    project_root = Path(__file__).parent.parent

    registry = SourceRegistry()
    registry.register("file", FileTaskSource)
    registry.register("generator", GeneratorTaskSource)
    registry.register("api", ApiTaskSource)

    platform = TaskPlatform()
    platform.add_source(registry.create("file", project_root / "source" / "tasks.json"))
    platform.add_source(registry.create("generator", lambda: create_generated_tasks(generated_count)))
    platform.add_source(registry.create("api", create_api_tasks(), "mock-api"))

    return platform


def run_demo(generated_count: int = 2) -> TaskQueue:
    platform = create_demo_platform(generated_count)
    tasks = platform.receive_tasks()

    print("[ДЕМОНСТРАЦИЯ] Прием задач из разных источников")
    print(f"[ДЕМОНСТРАЦИЯ] Количество источников: {len(platform.sources)}")

    for number, source in enumerate(platform.sources, start=1):
        print(
            f"[Источник {number}] {source.__class__.__name__}: "
            f"контракт соблюден = {isinstance(source, TaskSource)}"
        )

    for task in tasks:
        print(
            f"- {task.summary} | "
            f"description={task.description or 'не задано'} | payload={task.payload}"
        )

    print(f"[ДЕМОНСТРАЦИЯ] Всего принято задач: {len(tasks)}")
    return tasks
