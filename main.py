import asyncio
import logging
import random
from collections import defaultdict
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request

from config.settings import CommonSettings
from domain.models import SearchRequest, SearchResponse
from helpers.open_ai_helper import (
    generate_text,
    generate_alice_reply_async,
    ALICE_MAX_HISTORY_TURNS,
)
from helpers.timehelper import measure_time_async

app = FastAPI()

# In-memory store: user_id -> list of {role, content} dicts (excluding system message)
_alice_history: Dict[str, List[dict]] = defaultdict(list)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    if CommonSettings().DRY_MODE:
        return SearchResponse(
            answer="Сервер запущен в тестовом режиме. Запросы к OpenAI временно не выполняются",
            is_refusal=False,
            is_success=False
        )
    result = generate_text(request.prompt, model=request.model)
    logging.info(f"Запрос из источника {request.source.value} к модели {request.model}")
    response = SearchResponse(
        answer=result.refusal or result.content,
        is_refusal=result.refusal is not None,
        is_success=True
    )
    return response


def _extract_alice_question(request_data: dict) -> str:
    request_section = request_data.get("request") or {}
    command = (request_section.get("command") or "").strip()
    utterance = (request_section.get("original_utterance") or "").strip()
    return command or utterance


@app.post("/alice")
async def answer_to_alice_user(request: Request) -> dict:
    request_data = await request.json()
    logging.info(str(request_data))
    if not isinstance(request_data, dict):
        logging.warning("Invalid Alice payload: expected JSON object")
        return {
            "version": "1.0",
            "response": {"text": "Ошибка формата запроса.", "end_session": True},
        }
    response = get_response_template(request_data)
    question = _extract_alice_question(request_data)
    if not question:
        response["response"]["text"] = "Спрашивайте!"
        return response
    user_id = request_data.get("session", {}).get("user_id") or "anonymous"
    answer = await ask(question, user_id)
    logging.info(f"answer: {answer}")
    response["response"]["text"] = answer
    return response


def get_response_template(request_data: dict) -> dict:
    return {
        'session': request_data.get('session', {}),
        'version': request_data.get('version', '1.0'),
        'response': {
            'end_session': False
        }
    }


@measure_time_async
async def ask(question: str, user_id: str) -> str:
    if CommonSettings().DRY_MODE:
        await asyncio.sleep(random.randint(3, 25))
        return "Ответик пришел"
    else:
        history = _alice_history[user_id]
        result = await generate_alice_reply_async(question, history=history)
        answer = (result.refusal or result.content or "").strip()
        if not answer:
            answer = "Не смогла сформулировать ответ, попробуйте переформулировать вопрос."
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        # Keep only last N turns (each turn = 2 messages)
        if len(history) > ALICE_MAX_HISTORY_TURNS * 2:
            _alice_history[user_id] = history[-(ALICE_MAX_HISTORY_TURNS * 2):]
        return answer


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    uvicorn.run(app, host="0.0.0.0", port=7999)

# Запрос в облачной функции яндекса:
# def handler(event, context):
#     response = requests.post(url="address/alice", json=event)
#     return response.json()
