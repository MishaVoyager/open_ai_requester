---
name: restart-services
description: Пересобрать и перезапустить open_ai_requester (FastAPI + nginx) через Docker Compose. Использовать после правок конфигурации или кода для деплоя на mishavoyager.fyi.
---

# Restart services

## Алгоритм

1. Рабочая директория: `/root/projects/open_ai_requester`
2. Проверить наличие `.env`
3. Выполнить:

```bash
bash .cursor/skills/restart-services/scripts/restart-services.sh
```

4. Проверить:
   - `curl -sk https://mishavoyager.fyi/` → `{"Hello":"World"}`
   - `curl -sk https://mishavoyager.fyi/health` → `ok`

## Логи

```bash
docker compose logs -f
docker compose logs -f app
docker compose logs -f nginx
```
