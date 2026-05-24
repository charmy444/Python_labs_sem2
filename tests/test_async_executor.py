import asyncio
import pytest
from src.app.executor import AsyncExecutor
from src.domain.task import Task

class MockHandler:
    def __init__(self):
        self.handled_tasks = []

    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0.01)
        self.handled_tasks.append(task)

@pytest.mark.asyncio
async def test_executor_processes_tasks():
    handler = MockHandler()
    async with AsyncExecutor(worker_count=2) as executor:
        executor.register_handler("test_action", handler)
        
        task1 = Task(id="t1", payload={"action": "test_action"}, description="desc 1")
        task2 = Task(id="t2", payload={"action": "test_action"}, description="desc 2")
        
        await executor.submit(task1)
        await executor.submit(task2)
        
    assert len(handler.handled_tasks) == 2
    assert task1.status == "completed"
    assert task2.status == "completed"

@pytest.mark.asyncio
async def test_executor_handles_errors():
    class ErrorHandler:
        async def handle(self, task: Task) -> None:
            raise ValueError("Test error")

    async with AsyncExecutor(worker_count=1) as executor:
        executor.register_handler("error_action", ErrorHandler())
        task = Task(id="te", payload={"action": "error_action"}, description="desc error")
        await executor.submit(task)

    assert task.status == "blocked"

@pytest.mark.asyncio
async def test_executor_uses_default_handler():
    default_handler = MockHandler()
    async with AsyncExecutor(worker_count=1) as executor:
        executor.register_handler("default", default_handler)
        task = Task(id="td", payload={"action": "unknown"}, description="desc default")
        await executor.submit(task)

    assert len(default_handler.handled_tasks) == 1
    assert task.status == "completed"
