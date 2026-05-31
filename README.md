# open_ai_requester

HTTP-сервис на FastAPI для запросов к OpenAI: универсальный поиск (`/search`) и навык Яндекс.Алисы (`/alice`). В продакшене доступен по HTTPS через nginx на домене **mishavoyager.fyi**.

Репозиторий: `/root/projects/open_ai_requester`

## Структура

```
.
├── main.py                 # FastAPI-приложение (uvicorn :7999)
├── docker-compose.yml      # Docker Compose: app + nginx
├── Dockerfile
├── nginx.conf              # HTTPS, прокси на app:7999 и Spotify OAuth
├── requirements.txt        # runtime-зависимости
├── requirements-dev.txt    # mypy, pytest
├── .env.example            # шаблон переменных окружения
├── config/
│   └── settings.py
├── domain/
│   └── models.py
└── helpers/
    ├── open_ai_helper.py
    ├── tghelper.py
    ├── texthelper.py
    └── timehelper.py
```

## Быстрый старт

```bash
cd /root/projects/open_ai_requester
cp .env.example .env
# заполните OPENAI_API_KEY
docker compose up -d --build
```

Проверка:

```bash
curl -sk https://mishavoyager.fyi/
curl -sk https://mishavoyager.fyi/health   # Spotify OAuth health (pet_project bot)
docker compose ps
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Health check. Ответ: `{"Hello":"World"}` |
| `POST` | `/search` | Запрос к OpenAI (`prompt`, опционально `model`, `source`) |
| `POST` | `/alice` | Webhook навыка Яндекс.Алисы |

URL для Алисы: `https://mishavoyager.fyi/alice`.

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `OPENAI_API_KEY` | да | Ключ OpenAI |
| `DRY_MODE` | да | `true` — без реальных запросов к OpenAI |

## nginx

- Домен: **mishavoyager.fyi**
- SSL: `/etc/letsencrypt/live/mishavoyager.fyi/` на хосте
- `/` → FastAPI (`app:7999`)
- `/callback`, `/health` → Spotify OAuth бота на хосте (`host.docker.internal:8888`)

## Локальная разработка

```bash
pip install -r requirements-dev.txt
python -m main
```

Сервис слушает `http://0.0.0.0:7999`.

## Типизация и тесты

```bash
pip install -r requirements-dev.txt
mypy .
pytest
```
