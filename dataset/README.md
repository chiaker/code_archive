# Demo dataset для индексатора

Набор `.py`-файлов для проверки индексатора и живой демонстрации API.

## Состав

- **`taskflow/`** — связный учебный проект «бэкенд таск-менеджера» (~55 файлов):
  - `models/` — доменные модели (User, Project, Task, Comment, Tag, Attachment, Notification);
  - `repositories/` — слой доступа к данным (generic-репозиторий + по сущностям);
  - `services/` — бизнес-логика (auth, users, tasks, projects, поиск, async-уведомления);
  - `schemas/` — схемы сериализации;
  - `api/` — HTTP-роуты и зависимости;
  - `utils/` — текст, даты, валидаторы, пагинация;
  - `workers/` — async email-воркер, cleanup-воркер;
  - `integrations/` — webhooks, Slack;
  - `tests/` — модульные и async-тесты;
  - `cli.py`, `config.py`, `constants.py`, `exceptions.py`, `logging_setup.py`.
- **`src/`, `tests/`** — исходный мини-проект.
- **`broken.py`** — намеренно битый файл для проверки устойчивости индексатора.

## Что специально заложено для демонстрации

- классы, методы, `@property`, `@classmethod`;
- обычные и **async**-функции (`services/notification_service.py`, `workers/email_worker.py`);
- **вложенные** функции (`services/auth_service.py` → `issue`/`encode`, `search_service.py`);
- docstring'и в разных вариантах (и файлы/функции без них);
- **одинаковые имена файлов** в разных папках (`__init__.py`, `utils.py`) — проверка дедупликации;
- один **битый** файл — индексатор его пропускает с предупреждением, не падая.

## Индексация

```bash
python -m app.indexer dataset/ --db code_index.db
```

Ориентировочно: ~62 проиндексированных файла, ~190 определений (классы + функции).
Точные цифры смотрите в `GET /api/stats` после индексации.
