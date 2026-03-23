from collections.abc import Callable, Iterable

from src.domain.task import Task, make_task


class GeneratorTaskSource:
    def __init__(self, generator_func: Callable[[], Iterable[object]]):
        self.generator_func = generator_func

    def get_tasks(self) -> list[Task]:
        return [make_task(item) for item in self.generator_func()]
