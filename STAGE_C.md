# Этап C: бонусы, тесты и Docker (роль 3)

Кратко о том, что я сделала на этапе C — добавила все бонусные возможности поверх API из этапа B, покрыла проект тестами и собрала `Dockerfile`.

## Что реализовано

Все бонусы из `plan.md` доведены до рабочего состояния, переиспользуя слой `crud` из этапа B (новые запросы добавлены туда же, эндпоинты остались тонкими).

### 1. Эндпоинт `GET /api/stats`

Сводная статистика по всей базе. Один запрос на число файлов и один сгруппированный (`GROUP BY kind`) на определения — без четырёх отдельных `COUNT`.

- [app/crud.py](app/crud.py) — `get_stats()`
- [app/schemas.py](app/schemas.py) — схема `StatsOut`
- [app/main.py](app/main.py) — эндпоинт

Пример ответа на нашем датасете:

```json
{"files": 6, "functions": 12, "classes": 4, "definitions": 16}
```

На пустой базе вернёт нули, а не 500.

### 2. Фильтр поиска `?type=function|class`

Необязательный параметр у `GET /api/search`. Если не передан — поиск как раньше. Допустимые значения ограничены регуляркой `^(function|class)$` на уровне `Query`, поэтому мусорное значение даёт **422**, а не тихо ломает запрос.

### 3. Пагинация `?limit=&offset=`

Добавлена на оба списочных эндпоинта — `GET /api/files` и `GET /api/search`.

- `limit` — необязательный (`ge=1`); если не передан, возвращаются все строки (поведение этапа B сохранено).
- `offset` — по умолчанию `0` (`ge=0`).

Логика пагинации живёт в `crud.list_files` и `crud.search_definitions`, эндпоинты только пробрасывают параметры.

## Тесты

Папка [tests](tests). Запуск — просто `pytest` (конфиг в [pytest.ini](pytest.ini): `pythonpath=.`, `testpaths=tests`).

- [tests/conftest.py](tests/conftest.py) — фикстуры: на каждый тест своя временная SQLite-база (через `create_session_factory`), переопределение зависимости `get_db` у FastAPI и `TestClient`. Фикстура `seeded` кладёт детерминированные данные (`auth.py` с классом и двумя функциями + `empty.py` без определений).
- [tests/test_indexer.py](tests/test_indexer.py) — проверяет индексатор на мини-проекте [tests/sample_code](tests/sample_code): извлечение функций/классов/async/вложенных/методов, номера строк и docstring, что **битый файл пропускается, а не роняет прогон**, уникальность одинаковых имён файлов из разных папок и идемпотентность повторной индексации.
- [tests/test_api.py](tests/test_api.py) — по каждому эндпоинту happy-path плюс граничные случаи.

Особое внимание — на ключевой критерий кейса:

- пустой результат `GET /api/files`, `GET /api/search` → `[]` и статус **200**, никогда не 500;
- файл без определений → `definitions: []`;
- несуществующий файл в `/structure` → **404**;
- `/api/stats` на пустой базе → нули.

Итог прогона: **20 passed**.

## Docker

[Dockerfile](Dockerfile) на базе `python:3.12-slim`. Зависимости ставятся раньше кода (кэш слоёв). На старте контейнера сначала индексируется `dataset/`, затем поднимается uvicorn на `0.0.0.0:8000`. Папку `dataset/` можно как запечь в образ, так и примонтировать на запуске. Лишнее (`tests/`, `*.db`, кэши) исключено через [.dockerignore](.dockerignore).

```bash
docker build -t code-archive .
docker run -p 8000:8000 code-archive
# Swagger: http://127.0.0.1:8000/docs

# свой датасет вместо запечённого:
docker run -p 8000:8000 -v "$(pwd)/dataset:/app/dataset" code-archive
```

## Итоговая проверка всех эндпоинтов

```bash
curl http://127.0.0.1:8000/api/files
curl "http://127.0.0.1:8000/api/files?limit=5&offset=0"
curl http://127.0.0.1:8000/api/files/<имя>.py/structure
curl "http://127.0.0.1:8000/api/search?q=auth"
curl "http://127.0.0.1:8000/api/search?q=user&type=class"
curl "http://127.0.0.1:8000/api/search?q=user&limit=10&offset=0"
curl http://127.0.0.1:8000/api/stats
pytest        # 20 passed
```

## Что осталось команде (вместе)

- `README.md` (описание схемы БД, обоснования, примеры запросов) — общая работа.
- Сборка веток в общий репозиторий, сценарий 7-минутной демо.
