#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/projects/open_ai_requester"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found in $ROOT" >&2
  exit 1
fi

docker compose up --build -d
docker compose ps

if curl -sfk https://mishavoyager.fyi/ >/dev/null; then
  echo "OK: https://mishavoyager.fyi/ is reachable"
else
  echo "WARN: https://mishavoyager.fyi/ is not reachable yet" >&2
fi
