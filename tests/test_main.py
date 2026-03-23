import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import main


def test_main_exit(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "3")

    result = main([])
    captured = capsys.readouterr()

    assert result == 0
    assert "Выход из программы" in captured.out


def test_main_with_invalid_start_value(capsys):
    result = main(["--generated-count", "-1"])
    captured = capsys.readouterr()

    assert result == 1
    assert "Количество задач не может быть отрицательным" in captured.out


def test_main_run_demo_from_menu(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    answers = iter(["1", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = main([])
    captured = capsys.readouterr()

    assert result == 0
    assert "[ДЕМОНСТРАЦИЯ]" in captured.out
    assert "Выход из программы" in captured.out


def test_main_without_tty_runs_demo_once(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    result = main(["--generated-count", "4"])
    captured = capsys.readouterr()

    assert result == 0
    assert "[ДЕМОНСТРАЦИЯ]" in captured.out
    assert "Всего принято задач: 8" in captured.out
