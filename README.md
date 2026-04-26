# Лабораторная работа №2
# Модель задачи: дескрипторы и `@property`

## Описание лабораторной работы

Проект развивает первую лабораторную работу

В реализации добавлены:

- пользовательские `data descriptor` для валидации `id`, `description`, `priority`, `payload` и `status`;
- `@property` для защищенного `created_at` и вычисляемого признака `is_ready`;
- защита инвариантов состояния и допустимых переходов статуса;
- специализированные исключения `TaskValidationError`, `TaskStateError`, `TaskTransitionError`;
- пример `non-data descriptor` через атрибут `summary`;
- сохранение совместимости с источниками задач из первой лабораторной.

## Основные требования, которые покрывает проект

- корректная инкапсуляция внутреннего состояния через приватные поля;
- предотвращение некорректных состояний задачи;
- разделение публичного API и внутренней реализации;
- демонстрация различий между `data` и `non-data` descriptor;
- наличие аннотаций типов и документации.

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
│       ├── file_source.py
│       ├── generator_source.py
│       ├── api_source.py
│       └── tasks.json
├── tests/
│   ├── __init__.py
│   ├── test_task.py
│   ├── test_task_collection.py
│   ├── test_sources.py
│   ├── test_registry.py
│   ├── test_platform.py
│   ├── test_simulation.py
│   └── test_main.py
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── README.md
```

## Доменная модель `Task`

`Task` теперь поддерживает следующие атрибуты:

- `id` — идентификатор задачи;
- `description` — описание задачи;
- `priority` — приоритет от `1` до `5`;
- `status` — один из `pending`, `in_progress`, `blocked`, `completed`, `cancelled`;
- `created_at` — время создания задачи, доступное только для чтения;
- `payload` — полезная нагрузка задачи;
- `is_ready` — вычисляемое свойство, показывающее готовность задачи к исполнению;
- `summary` — пример `non-data descriptor`, который можно затенить атрибутом экземпляра.

Поддерживаются переходы статусов:

- `pending -> in_progress | cancelled`
- `in_progress -> blocked | completed | cancelled`
- `blocked -> in_progress | cancelled`
- `completed` и `cancelled` являются терминальными состояниями

Задача не может перейти в рабочий статус (`in_progress`, `blocked`, `completed`), если у нее отсутствует описание или `payload`.

## Исключения

- `TaskValidationError` — ошибка валидации атрибутов;
- `TaskStateError` — нарушение инвариантов состояния;
- `TaskTransitionError` — запрещенный переход между статусами.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Как правильно запускать

### Основной запуск

```bash
python3 -m src.main
```


После запуска программа показывает консольное меню:

- `1` — запустить демонстрацию приема задач;
- `2` — изменить количество задач, которые будет возвращать генератор;
- `3` — выйти из программы.

CLI вынесен в `src/app/cli.py` и работает через `argparse` и простое текстовое меню. JSON для файлового источника лежит в `src/source/tasks.json`.

Если программа запускается без интерактивного ввода, она не показывает меню, а сразу выполняет один демонстрационный прогон. Это удобно для Docker-контейнера.

Во время демонстрации выводятся:

- источник каждой группы задач;
- `summary` задачи;
- описание задачи;
- текущее состояние и полезная нагрузка.

### Запуск тестов

```bash
python3 -m pytest tests/ -v
```

### Запуск в Docker

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

## Что проверяют тесты

- совместимость со старыми источниками задач;
- валидацию атрибутов через дескрипторы;
- корректность вычисляемых свойств;
- допустимые и недопустимые переходы статусов;
- различие между `data` и `non-data descriptor`.
