from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from datetime import UTC, datetime
from typing import Any, ClassVar


class TaskError(Exception):
    """Базовое исключение доменной модели задачи."""


class TaskValidationError(TaskError, ValueError):
    """Ошибка валидации атрибутов задачи."""


class TaskStateError(TaskError, ValueError):
    """Ошибка нарушения инвариантов состояния задачи."""


class TaskTransitionError(TaskStateError):
    """Ошибка недопустимого перехода статуса."""


class ValidatedDescriptor:
    """Базовый data descriptor с хранением данных во внутреннем атрибуте."""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[object] | None = None) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: Any) -> None:
        normalized = self.validate(instance, value)
        setattr(instance, self.storage_name, normalized)

    def validate(self, instance: object, value: Any) -> Any:
        raise NotImplementedError


class IdentifierDescriptor(ValidatedDescriptor):
    """Валидирует идентификатор задачи."""

    def validate(self, instance: object, value: Any) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise TaskValidationError("У задачи должен быть непустой id")
        return normalized


class DescriptionDescriptor(ValidatedDescriptor):
    """Нормализует описание задачи."""

    def validate(self, instance: object, value: Any) -> str:
        if value is None:
            normalized = ""
        else:
            normalized = str(value).strip()
        return normalized


class PriorityDescriptor(ValidatedDescriptor):
    """Проверяет числовой приоритет задачи."""

    def validate(self, instance: object, value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TaskValidationError("Приоритет должен быть целым числом")
        if not 1 <= value <= 5:
            raise TaskValidationError("Приоритет должен быть в диапазоне от 1 до 5")
        return value


class PayloadDescriptor(ValidatedDescriptor):
    """Гарантирует наличие полезной нагрузки задачи."""

    def validate(self, instance: object, value: Any) -> Any:
        if value is None:
            raise TaskValidationError("Payload задачи не может быть пустым")
        return value


class StatusDescriptor(ValidatedDescriptor):
    """Валидирует статус и разрешенные переходы между статусами."""

    def validate(self, instance: object, value: Any) -> str:
        if not isinstance(instance, Task):
            raise TaskStateError("StatusDescriptor может использоваться только в Task")

        normalized = str(value).strip().lower()
        if normalized not in instance.ALLOWED_STATUSES:
            raise TaskValidationError(
                f"Недопустимый статус '{value}'. "
                f"Разрешены: {', '.join(sorted(instance.ALLOWED_STATUSES))}"
            )

        current_status = getattr(instance, self.storage_name, None)
        if current_status is None:
            instance.ensure_status_invariants(normalized)
            return normalized

        allowed_next = instance.ALLOWED_TRANSITIONS[current_status]
        if normalized not in allowed_next:
            raise TaskTransitionError(
                f"Переход из статуса '{current_status}' в '{normalized}' запрещен"
            )

        instance.ensure_status_invariants(normalized)
        return normalized


class TaskSummaryDescriptor:
    """Пример non-data descriptor: его можно затенить атрибутом экземпляра."""

    def __get__(self, instance: Task | None, owner: type[Task] | None = None) -> str | "TaskSummaryDescriptor":
        if instance is None:
            return self
        return (
            f"{instance.id} [{instance.status}] "
            f"priority={instance.priority} ready={instance.is_ready}"
        )


class Task:
    """Доменная модель задачи с защищенным внутренним состоянием."""

    ALLOWED_STATUSES: ClassVar[frozenset[str]] = frozenset(
        {"pending", "in_progress", "blocked", "completed", "cancelled"}
    )
    ALLOWED_TRANSITIONS: ClassVar[dict[str, frozenset[str]]] = {
        "pending": frozenset({"pending", "in_progress", "cancelled"}),
        "in_progress": frozenset({"in_progress", "blocked", "completed", "cancelled"}),
        "blocked": frozenset({"blocked", "in_progress", "cancelled"}),
        "completed": frozenset({"completed"}),
        "cancelled": frozenset({"cancelled"}),
    }

    id = IdentifierDescriptor()
    description = DescriptionDescriptor()
    priority = PriorityDescriptor()
    payload = PayloadDescriptor()
    status = StatusDescriptor()
    summary = TaskSummaryDescriptor()

    def __init__(
        self,
        id: str,
        payload: Any,
        description: str | None = None,
        priority: int = 3,
        status: str = "pending",
        created_at: datetime | str | None = None,
    ) -> None:
        self.id = id
        self.payload = payload
        self.description = description
        self.priority = priority
        self._created_at = self._normalize_created_at(created_at)
        self.status = status

    @staticmethod
    def _normalize_created_at(value: datetime | str | None) -> datetime:
        if value is None:
            return datetime.now(UTC)

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError as error:
                raise TaskValidationError(
                    "created_at должен быть datetime или ISO-строкой"
                ) from error

        raise TaskValidationError("created_at должен быть datetime или ISO-строкой")

    @property
    def created_at(self) -> datetime:
        """Время создания доступно только на чтение."""

        return self._created_at

    @property
    def is_ready(self) -> bool:
        """Готова ли задача к исполнению с точки зрения инвариантов."""

        return self._has_execution_data and self.status not in {"completed", "cancelled"}

    @property
    def _has_execution_data(self) -> bool:
        return bool(self.description.strip()) and self.payload is not None

    def ensure_status_invariants(self, next_status: str) -> None:
        if next_status in {"in_progress", "blocked", "completed"} and not self._has_execution_data:
            raise TaskStateError(
                "Задача должна иметь описание и payload перед переходом в рабочий статус"
            )

    def start(self) -> None:
        self.status = "in_progress"

    def block(self) -> None:
        self.status = "blocked"

    def complete(self) -> None:
        self.status = "completed"

    def cancel(self) -> None:
        self.status = "cancelled"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "payload": self.payload,
            "is_ready": self.is_ready,
        }

    def __repr__(self) -> str:
        return (
            "Task("
            f"id={self.id!r}, "
            f"status={self.status!r}, "
            f"priority={self.priority!r}, "
            f"description={self.description!r}"
            ")"
        )


class TaskQueue:
    """Пользовательская коллекция задач с повторной итерацией и ленивыми фильтрами."""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        self.tasks: list[Task] = []
        if tasks is not None:
            self.extend(tasks)

    def __getitem__(self, key: int | slice) -> Task | list[Task]:
        return self.tasks[key]

    def __iter__(self) -> Iterator[Task]:
        for task in self.tasks:
            yield task

    def __len__(self) -> int:
        return len(self.tasks)

    def add(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("В очередь можно добавлять только экземпляры Task")
        self.tasks.append(task)

    def extend(self, tasks: Iterable[Task]) -> None:
        for task in tasks:
            self.add(task)

    def filter_by_status(self, status: str) -> Iterator[Task]:
        normalized_status = status.strip().lower()
        if normalized_status not in Task.ALLOWED_STATUSES:
            raise TaskValidationError(
                f"Недопустимый статус фильтра '{status}'. "
                f"Разрешены: {', '.join(sorted(Task.ALLOWED_STATUSES))}"
            )

        for task in self:
            if task.status == normalized_status:
                yield task

    def filter_by_priority(self, priority: int) -> Iterator[Task]:
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise TaskValidationError("Приоритет фильтра должен быть целым числом")
        if not 1 <= priority <= 5:
            raise TaskValidationError("Приоритет фильтра должен быть в диапазоне от 1 до 5")

        for task in self:
            if task.priority == priority:
                yield task


TaskCollection = TaskQueue


def make_task(raw_task: object) -> Task:
    if isinstance(raw_task, Task):
        return raw_task

    if isinstance(raw_task, Mapping):
        if "id" not in raw_task or "payload" not in raw_task:
            raise TaskValidationError("Словарь задачи должен содержать id и payload")
        return Task(
            id=raw_task["id"],
            payload=raw_task["payload"],
            description=raw_task.get("description"),
            priority=raw_task.get("priority", 3),
            status=raw_task.get("status", "pending"),
            created_at=raw_task.get("created_at"),
        )

    if hasattr(raw_task, "id") and hasattr(raw_task, "payload"):
        return Task(
            id=getattr(raw_task, "id"),
            payload=getattr(raw_task, "payload"),
            description=getattr(raw_task, "description", None),
            priority=getattr(raw_task, "priority", 3),
            status=getattr(raw_task, "status", "pending"),
            created_at=getattr(raw_task, "created_at", None),
        )

    raise TaskValidationError("Неподходящий формат задачи")
