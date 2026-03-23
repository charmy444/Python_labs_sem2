from collections.abc import Sequence

from src.app.cli import main as package_main


def main(argv: Sequence[str] | None = None) -> int:
    return package_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
