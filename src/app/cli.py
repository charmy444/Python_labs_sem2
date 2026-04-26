import argparse
import sys
from collections.abc import Sequence

from src.app.demo import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Прием и валидация задач с использованием дескрипторов"
    )
    parser.add_argument(
        "--generated-count",
        type=int,
        default=2,
        help="Количество задач, которые должен вернуть генератор",
    )
    return parser


def read_generated_count(current_count: int) -> int:
    raw_value = input(
        f"Введите количество задач от генератора (сейчас {current_count}): "
    ).strip()

    if not raw_value:
        return current_count

    try:
        new_count = int(raw_value)
    except ValueError:
        print("Ошибка: нужно ввести целое число")
        return current_count

    if new_count < 0:
        print("Ошибка: количество задач не может быть отрицательным")
        return current_count

    return new_count


def show_menu(current_count: int) -> None:
    print()
    print("Меню:")
    print(f"1. Запустить демонстрацию (генератор: {current_count})")
    print("2. Изменить количество задач генератора")
    print("3. Выйти")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.generated_count < 0:
        print("Ошибка: Количество задач не может быть отрицательным")
        return 1

    generated_count = args.generated_count

    if not sys.stdin.isatty():
        run_demo(generated_count)
        return 0

    while True:
        show_menu(generated_count)
        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            run_demo(generated_count)
        elif choice == "2":
            generated_count = read_generated_count(generated_count)
        elif choice == "3":
            print("Выход из программы")
            return 0
        else:
            print("Ошибка: выберите пункт 1, 2 или 3")

    return 0
