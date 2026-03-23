from typing import Any

from src.contacts.task_source import TaskSource


class SourceRegistry:
    def __init__(self) -> None:
        self.source_classes: dict[str, type[object]] = {}

    def register(self, name: str, source_class: type[object]) -> None:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Имя источника не должно быть пустым")
        if normalized_name in self.source_classes:
            raise ValueError(f"Источник {normalized_name} уже зарегистрирован")
        if not issubclass(source_class, TaskSource):
            raise TypeError("Класс не реализует контракт TaskSource")
        self.source_classes[normalized_name] = source_class

    def create(self, name: str, *args: Any, **kwargs: Any) -> TaskSource:
        if name not in self.source_classes:
            raise KeyError(f"Источник {name} не зарегистрирован")

        source = self.source_classes[name](*args, **kwargs)
        if not isinstance(source, TaskSource):
            raise TypeError("Объект не реализует контракт TaskSource")
        return source
