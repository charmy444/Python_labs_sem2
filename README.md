# Лабораторная работа №3
# Очередь задач: итераторы и генераторы

## Описание

Проект развивает предыдущие лабораторные в общей предметной области платформы обработки задач.

В проекте сохранены:

- контракт `TaskSource` из лабораторной 1;
- доменная модель `Task` с дескрипторами и `property` из лабораторной 2;
- работа с объектами `Task`, а не со словарями на уровне коллекции.

В лабораторной 3 добавлена очередь задач `TaskQueue`.

## Что реализовано

- пользовательская коллекция `TaskQueue`;
- поддержка `for`, `list`, `sum`, `len`, индексирования;
- повторная итерация по очереди;
- ленивые фильтры `filter_by_status()` и `filter_by_priority()`;
- фильтрация через генераторы.

Для совместимости со старым кодом сохранён `TaskCollection` как алиас для `TaskQueue`.

## Структура проекта

```text
.
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── app/
│   │   ├── cli.py
│   │   ├── demo.py
│   │   ├── platform.py
│   │   └── registry.py
│   ├── contacts/
│   │   └── task_source.py
│   ├── domain/
│   │   └── task.py
│   └── source/
│       ├── api_source.py
│       ├── file_source.py
│       ├── generator_source.py
│       └── tasks.json
├── tests/
│   ├── test_main.py
│   ├── test_platform.py
│   ├── test_registry.py
│   ├── test_simulation.py
│   ├── test_sources.py
│   ├── test_task.py
│   └── test_task_collection.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── README.md
```

## Пример использования

```python
queue = TaskQueue()
queue.add(task)

for current_task in queue:
    print(current_task.id)

completed = list(queue.filter_by_status("completed"))
high_priority = list(queue.filter_by_priority(5))
```

## Запуск

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск программы:

```bash
python3 -m src.main
```

Запуск тестов:

```bash
python3 -m pytest tests/ -v
```

## Запуск в Docker

Сборка образа:

```bash
docker build -t lab1-task-platform .
```

Запуск контейнера:

```bash
docker run -it --rm lab1-task-platform
```

Запуск без интерактивного режима:

```bash
docker run --rm lab1-task-platform
```

Запуск тестов внутри контейнера:

```bash
docker run --rm lab1-task-platform python -m pytest tests/ -v
```

Проверка покрытия:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```

## Что проверяют тесты

- валидацию и инварианты `Task`;
- работу источников задач;
- повторную итерацию по `TaskQueue`;
- корректную работу фильтров по статусу и приоритету;
- совместимость очереди со стандартными конструкциями Python;
- интеграцию очереди в `TaskPlatform`.
