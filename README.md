# open_ai_requester

HTTP-сервис на FastAPI для запросов к OpenAI: универсальный поиск (`/search`) и навык Яндекс.Алисы (`/alice`). В продакшене доступен по HTTPS через nginx на домене **mishavoyager.fyi**.

## Структура репозитория

```
.
├── main.py              # FastAPI-приложение, точка входа (uvicorn :7999)
├── compose.yml          # Docker Compose: app + nginx
├── Dockerfile           # Образ приложения (Python 3.12)
├── nginx.conf           # HTTPS, редирект 80→443, прокси на app:7999
├── requirements.txt     # Python-зависимости
├── mypy.ini             # Настройки mypy
├── config/
│   └── settings.py      # OPENAI_API_KEY, DRY_MODE из .env
├── domain/
│   └── models.py        # SearchRequest, SearchResponse, Source
└── helpers/
    ├── open_ai_helper.py  # Клиент OpenAI (sync/async, whisper, vision)
    ├── tghelper.py        # Утилиты для Telegram/aiogram (клавиатуры, пагинация)
    ├── texthelper.py      # Текстовые хелперы
    └── timehelper.py      # Декоратор замера времени async-функций
```

Вспомогательные файлы вне основного деплоя: `someee.py` (локальный тест запроса к `/search`).

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Проверка, что сервис живой. Ответ: `{"Hello":"World"}` |
| `POST` | `/search` | Текстовый запрос к OpenAI (JSON: `prompt`, опционально `model`, `source`) |
| `POST` | `/alice` | Webhook для навыка Алисы (тело — JSON от Яндекса) |

Пример `/search`:

```json
{
  "prompt": "Привет",
  "model": "gpt-4o-mini",
  "source": "OTHER"
}
```

Для Алисы в облачной функции Яндекса укажите URL: `https://mishavoyager.fyi/alice`.

## Переменные окружения

Файл `.env` (не в git):

| Переменная | Описание |
|------------|----------|
| `OPENAI_API_KEY` | Ключ OpenAI |
| `DRY_MODE` | `true` — без реальных запросов к OpenAI (тестовые ответы) |

## Запуск

### Docker Compose (продакшен)

```bash
docker compose up -d --build
```

Контейнеры:

- **voyager_server** — FastAPI на порту `7999`
- **voyager_nginx** — nginx на `80`/`443`, SSL из `/etc/letsencrypt`, прокси `/callback` и `/health` на Spotify OAuth бота (`host:8888`)

Проверка:

```bash
curl -sk https://mishavoyager.fyi/
docker compose ps
```

### Локально без Docker

```bash
pip install -r requirements.txt
python -m main
```

Сервис слушает `http://0.0.0.0:7999`.

## SSL и домен

- Домен: **mishavoyager.fyi**
- Сертификаты Let's Encrypt на хосте: `/etc/letsencrypt/live/mishavoyager.fyi/`
- Выпуск/обновление (порты 80/443 свободны, nginx остановлен):

```bash
certbot certonly --standalone -d mishavoyager.fyi
```

## Зависимости

Основные: FastAPI, uvicorn, OpenAI SDK, pydantic-settings. В `requirements.txt` также aiogram, SQLAlchemy, alembic, asyncpg — задел под Telegram-бота и БД; в текущем `main.py` не используются.

## Типизация

```bash
mypy .
```
