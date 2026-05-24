import asyncio
import logging
from src.contacts.handler import TaskHandler
from src.domain.task import Task

logger = logging.getLogger(__name__)

class LogHandler:
    """Обработчик, который просто логирует выполнение задачи."""
    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0.5)  # Симуляция работы
        logger.info(f"[LogHandler] Задача {task.id}: {task.description}")

class NotificationHandler:
    """Обработчик для отправки уведомлений."""
    async def handle(self, task: Task) -> None:
        await asyncio.sleep(1)  # Симуляция сетевой задержки
        channel = "unknown"
        if isinstance(task.payload, dict):
            channel = task.payload.get("channel", "unknown")
        logger.info(f"[NotificationHandler] Уведомление отправлено через {channel} для задачи {task.id}")

class OrderProcessingHandler:
    """Обработчик для обработки заказов."""
    async def handle(self, task: Task) -> None:
        await asyncio.sleep(1.5)  # Тяжелая операция
        order_id = "unknown"
        if isinstance(task.payload, dict):
            order_id = task.payload.get("order_id", "unknown")
        logger.info(f"[OrderProcessingHandler] Заказ {order_id} успешно обработан (задача {task.id})")
