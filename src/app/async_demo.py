import asyncio
import logging
import sys

from src.app.demo import create_demo_platform
from src.app.handlers import LogHandler, NotificationHandler, OrderProcessingHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def run_async_demo(generated_count: int = 2) -> None:
    """Запуск асинхронной демонстрации."""
    logger.info("=== Запуск асинхронной демонстрации Lab 4 ===")
    
    platform = create_demo_platform(generated_count)
    
    # Регистрация обработчиков
    platform.executor.register_handler("default", LogHandler())
    platform.executor.register_handler("send_notification", NotificationHandler())
    platform.executor.register_handler("process_order", OrderProcessingHandler())
    platform.executor.register_handler("generated_task", LogHandler())
    
    logger.info("Платформа готова. Начинаем асинхронную обработку...")
    
    await platform.run_async()
    
    logger.info("=== Асинхронная демонстрация завершена ===")

    logger.info("Финальные статусы задач:")
    for task in platform.task_queue:
        logger.info(f"- {task.id}: {task.status}")


if __name__ == "__main__":
    asyncio.run(run_async_demo())
