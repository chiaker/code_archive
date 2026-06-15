# План выполнения: Кейс 2 — «Архив кода»

## Контекст

Нужно с нуля собрать сервис «структурированный каталог кода»: Python-индексатор, который через модуль `ast` извлекает функции/классы/docstring из `.py`-файлов и кладёт в SQLite, плюс REST API на FastAPI с тремя эндпоинтами. Защита — 7 минут в ВКС: запуск сервиса, индексация датасета из 60 `.py`-файлов и живая демонстрация эндпоинтов на запросах экспертов.

Зафиксированные решения:
- **Слой БД:** SQLAlchemy ORM (вместо чистого `sqlite3`).
- **Бонусы (все):** `/api/stats`, фильтр поиска `?type=`, пагинация `?limit=&offset=`, `Dockerfile`.
- **Роли:** 3 человека, каждый пишет свой кусок кода; всё, что не код (README, презентация, демо, ответы экспертам, проверка воспроизводимости), делаем вместе.

Главный риск по критериям оценки: пустой результат должен возвращать `[]` (пустой массив), а **не** 500. Эксперты на защите почти гарантированно спрашивают про схему БД и индексы — ответы готовим заранее.

---

## Технологический стек

- Python 3.12
- FastAPI + uvicorn (веб-API)
- SQLAlchemy 2.x (ORM поверх SQLite)
- Стандартный модуль `ast` (парсинг кода) — без сторонних парсеров
- pytest + httpx/TestClient (тесты)
- curl / Postman (ручная проверка на защите)

`requirements.txt`:
```
fastapi
uvicorn[standard]
sqlalchemy
pytest
httpx
```

---

## Структура репозитория

```
archive/
├── app/
│   ├── __init__.py
│   ├── db.py          # engine, SessionLocal, Base, get_db()
│   ├── models.py      # ORM-модели File, Definition
│   ├── schemas.py     # Pydantic-модели ответов
│   ├── indexer.py     # обход директории + ast-парсинг + запись в БД
│   ├── crud.py        # запросы к БД (переиспользуются эндпоинтами)
│   └── main.py        # FastAPI app + 4 эндпоинта
├── tests/
│   ├── conftest.py    # фикстура тестовой БД + TestClient
│   ├── sample_code/   # 2-3 маленьких .py для тестов
│   ├── test_indexer.py
│   └── test_api.py
├── dataset/           # 60 .py-файлов от организаторов (кладём сюда)
├── code_index.db      # SQLite (в .gitignore)
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md          # описание схемы БД, запуск, обоснования
```

---

## Проектирование БД (SQLAlchemy ORM)

Две таблицы — `files` (один файл) и `definitions` (функции и классы, многие-к-одному к файлу). Тип определения хранится строкой (`function` / `class`), что напрямую обслуживает бонусный фильтр `?type=`.

`app/models.py`:
```python
class File(Base):
    __tablename__ = "files"
    id       = Column(Integer, primary_key=True)
    name     = Column(String, unique=True, index=True, nullable=False)  # имя файла
    path     = Column(String, nullable=False)                            # относительный путь
    definitions = relationship("Definition", back_populates="file",
                               cascade="all, delete-orphan")

class Definition(Base):
    __tablename__ = "definitions"
    id         = Column(Integer, primary_key=True)
    file_id    = Column(Integer, ForeignKey("files.id"), index=True, nullable=False)
    name       = Column(String, index=True, nullable=False)   # имя функции/класса
    kind       = Column(String, nullable=False)               # 'function' | 'class'
    line_start = Column(Integer, nullable=False)
    line_end   = Column(Integer, nullable=False)
    docstring  = Column(Text, nullable=True)
    file       = relationship("File", back_populates="definitions")
```

**Обоснование схемы (готовый ответ для защиты):**
- Нормализация на 2 таблицы убирает дублирование имени/пути файла в каждой строке определения.
- `index=True` на `files.name` — ускоряет `GET /api/files/{name}/structure` (поиск по имени).
- `index=True` на `definitions.name` — ускоряет `GET /api/search` по имени.
- `index=True` на `definitions.file_id` — ускоряет JOIN/выборку структуры файла.
- `kind` строкой, а не отдельными таблицами, — проще и достаточно для двух типов; напрямую даёт фильтр `?type=`.
- Поиск по docstring делаем через `LIKE` — для 60 файлов этого достаточно, FTS избыточен (зафиксировать в README).

---

## Часть А. Индексатор (`app/indexer.py`)

Алгоритм:
1. Принять путь к директории (CLI-аргумент, по умолчанию `dataset/`).
2. (Пере)создать схему БД; перед индексацией чистить таблицы, чтобы повторный запуск был идемпотентным.
3. Рекурсивно собрать `*.py` (`pathlib.Path.rglob`).
4. Для каждого файла: `tree = ast.parse(source)`, затем обойти **узлы верхнего уровня и вложенные** через `ast.walk`, отбирая `ast.FunctionDef`, `ast.AsyncFunctionDef`, `ast.ClassDef`.
5. Для каждого узла извлечь: `node.name`, `node.lineno` (start), `node.end_lineno` (end), `ast.get_docstring(node)`.
6. Записать `File` + связанные `Definition` в одной сессии, `commit`.

Ключевые детали и подводные камни:
- Оборачивать `ast.parse` в try/except `SyntaxError` — битый файл логируем и пропускаем, не падаем.
- Читать файлы как UTF-8.
- `end_lineno` доступен в Python 3.8+ (у нас 3.12) — ок.
- Запуск: `python -m app.indexer dataset/` (точка входа `if __name__ == "__main__":` с `argparse`).

---

## Часть Б. REST API (`app/main.py` + `app/crud.py`)

Все ответы — JSON через Pydantic-схемы. **Пустой результат → пустой массив `[]`, никогда не 500.** Несуществующий файл в `/structure` → 404 (это «не найдено», корректный код), а не 500.

Функции выборки выносим в `app/crud.py`, чтобы переиспользовать в эндпоинтах и тестах.

| Эндпоинт | Логика |
| --- | --- |
| `GET /api/files` | Список файлов + кол-во функций в каждом (через `func.count` / `len(file.definitions)` с фильтром `kind='function'`). Пагинация `?limit=&offset=`. |
| `GET /api/files/{name}/structure` | Все определения файла с `line_start/line_end/docstring/kind`. Нет файла → 404; файл без определений → `[]`. |
| `GET /api/search?q=&type=` | Определения, где `name LIKE %q%` ИЛИ `docstring LIKE %q%`, регистронезависимо (`func.lower`). Бонус `type=function|class`. Ничего не найдено → `[]`. Пагинация. |
| `GET /api/stats` *(бонус)* | Сводка: всего файлов, функций, классов. |

Pydantic-схемы (`app/schemas.py`): `FileSummary`, `DefinitionOut`, `FileStructureOut`, `SearchResult`, `StatsOut`.

`get_db()` — зависимость FastAPI, отдающая сессию SQLAlchemy с гарантированным закрытием.

Запуск: `uvicorn app.main:app --reload`. Swagger автоматически на `/docs` — показываем на защите.

---

## Бонусы

- **`/api/stats`** — три `COUNT`-запроса, одна Pydantic-схема.
- **`?type=`** — добавить опциональный query-параметр в `/api/search`, фильтр `Definition.kind == type`.
- **Пагинация** — `limit: int = 50`, `offset: int = 0` на `/api/files` и `/api/search`, `.limit().offset()` в запросе.
- **Dockerfile** — `python:3.12-slim`, `COPY`, `pip install -r requirements.txt`, индексация + `CMD uvicorn`. Документировать `docker build` + `docker run -p 8000:8000`.

---

## Тестирование (`tests/`)

- `conftest.py`: фикстура in-memory/временной SQLite + `TestClient(app)` с переопределением `get_db`.
- `test_indexer.py`: на `sample_code/` проверить, что функции/классы/строки/docstring извлекаются верно; битый файл не роняет индексатор.
- `test_api.py`: по каждому эндпоинту — happy path + **пустой результат возвращает `[]`, а не 500** (ключевой критерий); 404 на несуществующий файл; работа `?type=` и пагинации.
- Запуск: `pytest`.

---

## README.md (критерий «документация» + «воспроизводимость»)

Обязательные разделы:
1. Описание сервиса.
2. **Схема БД** (таблицы, поля, индексы) и **обоснование** — отдельным блоком, т.к. это главная тема вопросов.
3. Обоснование выбора SQLAlchemy ORM (показываем работу с ORM) и LIKE-поиска.
4. Установка: `pip install -r requirements.txt`.
5. Индексация: `python -m app.indexer dataset/`.
6. Запуск: `uvicorn app.main:app --reload` → `/docs`.
7. Примеры запросов (`curl`) по всем эндпоинтам, включая бонусные.
8. Запуск через Docker.

---

## Распределение ролей

3 человека. **Каждый пишет код** — у каждого своя зона в кодовой базе и финальное владение ею. **Всё, что не код, делаем вместе** (см. блок ниже).

### Код — зоны ответственности (каждый свой кусок)

| # | Роль | Что пишет (код) |
| - | ---- | --------------- |
| 1 | **Индексатор + БД** | `db.py`, `models.py`, `indexer.py`, схема и индексы, `requirements.txt`. Владелец вопроса про схему БД. |
| 2 | **API** | `main.py`, `crud.py`, `schemas.py` — три основных эндпоинта, корректные коды (`[]` вместо 500, 404). |
| 3 | **Бонусы + тесты** | `/api/stats`, `?type=`, пагинация; `tests/` (особенно проверка пустого результата `[]`), `Dockerfile`. |

### Делаем вместе (не код)

- `README.md` (описание схемы БД, обоснования, примеры запросов).
- GitHub-репозиторий и финальная сборка веток.
- Сценарий 7-минутной демо и распределение «кто что показывает».
- Подготовка ответов на вопросы экспертов (схема БД, индексы, выбор ORM/LIKE).
- Прогон индексатора на 60-файловом датасете и проверка воспроизводимости «из чистой среды».

> Координация: общий GitHub-репозиторий, ветки на роль, мелкие PR. Контракт между ролями (Pydantic-схемы и сигнатуры `crud`) согласуется в самом начале, чтобы API и индексатор разрабатывались параллельно. 
```
git checkout -b feature/indexer    # своя ветка под задачу 
# ... работа, коммиты ...
git push -u origin feature/indexer
```



---

## Порядок выполнения (вехи)

1. **Старт:** создать репозиторий, структуру папок, договориться о схеме БД и контрактах `crud`/схем. Положить датасет в `dataset/`.
2. **Параллельно:** роль 1 — индексатор+модели; роль 2 — каркас FastAPI на заглушках по согласованным схемам.
3. **Сборка:** подключить реальные `crud`-запросы к эндпоинтам, прогнать индексатор на датасете.
4. **Бонусы + тесты** параллельно с доводкой.
5. **README + Dockerfile** (запуск → индексация 60 файлов → живые запросы ко всем эндпоинтам → `/docs`).
6. **Финальная проверка воспроизводимости** из чистого окружения: `pip install -r requirements.txt` → индексация → запуск.

---

## Проверка 

```bash
pip install -r requirements.txt
python -m app.indexer dataset/
uvicorn app.main:app --reload
# в другом терминале:
curl http://127.0.0.1:8000/api/files
curl http://127.0.0.1:8000/api/files/<имя>.py/structure
curl "http://127.0.0.1:8000/api/search?q=auth"
curl "http://127.0.0.1:8000/api/search?q=auth&type=class"
curl "http://127.0.0.1:8000/api/files?limit=5&offset=0"
curl http://127.0.0.1:8000/api/stats
pytest        # все тесты зелёные, включая проверку "[] вместо 500"
```
Открыть `http://127.0.0.1:8000/docs` — Swagger со всеми эндпоинтами.

