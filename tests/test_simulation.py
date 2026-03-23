import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app.demo import create_demo_platform, create_generated_tasks, run_demo


def test_create_generated_tasks_default():
    tasks = create_generated_tasks()

    assert len(tasks) == 2
    assert tasks[0]["id"] == "generator-1"


def test_create_generated_tasks_custom_count():
    tasks = create_generated_tasks(4)

    assert len(tasks) == 4
    assert tasks[-1]["id"] == "generator-4"


def test_create_demo_platform():
    platform = create_demo_platform(3)

    assert len(platform.sources) == 3


def test_run_simulation(capsys):
    tasks = run_demo(2)
    captured = capsys.readouterr()

    assert len(tasks) == 6
    assert "[ДЕМОНСТРАЦИЯ]" in captured.out
