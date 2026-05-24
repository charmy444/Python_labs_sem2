import asyncio
import logging
from typing import Dict

from src.contacts.handler import TaskHandler
from src.domain.task import Task

logger = logging.getLogger(__name__)


class AsyncExecutor:
    """Асинхронный исполнитель задач с использованием очереди и обработчиков."""

    def __init__(self, worker_count: int = 3):
        self._queue: asyncio.Queue[Task] = asyncio.Queue()
        self._handlers: Dict[str, TaskHandler] = {}
        self._workers: list[asyncio.Task] = []
        self._worker_count = worker_count
        self._running = False

    def register_handler(self, action_name: str, handler: TaskHandler) -> None:
        """Регистрация обработчика для конкретного типа действия."""
        self._handlers[action_name] = handler
        logger.info(f"Зарегистрирован обработчик для действия: {action_name}")

    async def submit(self, task: Task) -> None:
        """Поместить задачу в очередь на выполнение."""
        await self._queue.put(task)
        logger.debug(f"Задача {task.id} добавлена в очередь")

    async def _worker(self, worker_id: int) -> None:
        """Воркер, извлекающий задачи из очереди."""
        logger.debug(f"Воркер {worker_id} запущен")
        while self._running or not self._queue.empty():
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                if not self._running:
                    break
                continue

            try:
                await self._process_task(task)
            finally:
                self._queue.task_done()
        logger.debug(f"Воркер {worker_id} завершил работу")

    async def _process_task(self, task: Task) -> None:
        """Поиск и вызов подходящего обработчика для задачи."""
        action = "default"
        if isinstance(task.payload, dict) and "action" in task.payload:
            action = task.payload["action"]

        handler = self._handlers.get(action)
        if not handler:
            handler = self._handlers.get("default")

        if handler:
            logger.info(f"Обработка задачи {task.id} (действие: {action})")
            try:
                if task.status == "pending":
                    task.start()
                await handler.handle(task)
                task.complete()
            except Exception as e:
                logger.error(f"Ошибка при обработке задачи {task.id}: {e}")
                try:
                    task.block()
                except Exception:
                    pass
        else:
            logger.warning(f"Нет обработчика для задачи {task.id} (действие: {action})")

    async def __aenter__(self) -> "AsyncExecutor":
        """Запуск исполнителя через контекстный менеджер."""
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i)) 
            for i in range(self._worker_count)
        ]
        logger.info(f"Исполнитель запущен с {self._worker_count} воркерами")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._running = False
        await self._queue.join()

        for worker in self._workers:
            worker.cancel()
            
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info("Исполнитель остановлен")
