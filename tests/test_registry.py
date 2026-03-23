import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from src.app.registry import SourceRegistry
from src.source.file_source import FileTaskSource


class WrongSource:
    pass


def test_register_valid_source():
    registry = SourceRegistry()

    registry.register("file", FileTaskSource)

    assert registry.source_classes["file"] == FileTaskSource


def test_register_invalid_source():
    registry = SourceRegistry()

    with pytest.raises(TypeError):
        registry.register("wrong", WrongSource)


def test_create_unregistered_source():
    registry = SourceRegistry()

    with pytest.raises(KeyError):
        registry.create("missing")


def test_register_duplicate_source_name():
    registry = SourceRegistry()
    registry.register("file", FileTaskSource)

    with pytest.raises(ValueError):
        registry.register("file", FileTaskSource)


def test_register_empty_source_name():
    registry = SourceRegistry()

    with pytest.raises(ValueError):
        registry.register("   ", FileTaskSource)
