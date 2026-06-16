# Этап B: REST API (роль 2)

Кратко о том, что я сделал на этапе B — слой REST API поверх готовой БД из этапа A.

## Что реализовано

Три новых файла в `app/`, переиспользующие слой БД из этапа A (`Base`, `get_db`, `init_db`):

- [app/schemas.py](app/schemas.py) — Pydantic-схемы ответов: `DefinitionOut`, `FileSummary`, `FileStructureOut`, `SearchResult`.
- [app/crud.py](app/crud.py) — запросы к БД: `list_files`, `get_file_structure`, `search_definitions`.
- [app/main.py](app/main.py) — FastAPI-приложение и три эндпоинта.

## Эндпоинты

| Эндпоинт | Что делает |
| --- | --- |
| `GET /api/files` | Список файлов + кол-во функций в каждом. Пустая БД → `[]`. |
| `GET /api/files/{name}/structure` | Полная структура файла (функции/классы, строки, docstring). Нет файла → **404**; файл без определений → `definitions: []`. |
| `GET /api/search?q=` | Определения, где имя или docstring содержит `q` (регистронезависимо, `LIKE`). Ничего не найдено → `[]`. |

Ключевое требование соблюдено: пустой результат → `[]`, никогда не 500; несуществующий файл → 404.

## Запуск

```bash
pip install -r requirements.txt
python -m app.indexer dataset/ --db code_index.db
uvicorn app.main:app --reload
```

Swagger со всеми эндпоинтами — на `/docs`.

## Вне зоны роли 2

`/api/stats`, фильтр `?type=`, пагинация, `Dockerfile`, тесты — это роль 3 и общая работа команды.
