import asyncio
import logging
import random

import uvicorn
from fastapi import FastAPI, Request

from config.settings import CommonSettings
from domain.models import SearchRequest, SearchResponse
from helpers.open_ai_helper import generate_text, generate_text_async, GPTModel
from helpers.timehelper import measure_time_async

app = FastAPI()


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


@app.post("/alice")
async def answer_to_alice_user(request: Request) -> dict:
    request_data = await request.json()
    logging.info(str(request_data))
    response = get_response_template(request_data)
    if not request_data['request']['original_utterance']:
        response["response"]["text"] = "Спрашивайте!"
        return response
    question: str = request_data['request']['original_utterance']
    user_id = request_data["session"]["user_id"]
    answer = await ask(question, user_id)
    logging.info(f"answer: {answer}")
    response["response"]["text"] = answer
    return response


def get_response_template(request_data: dict) -> dict:
    return {
        'session': request_data['session'],
        'version': request_data['version'],
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
        result = await generate_text_async(question, GPTModel.gpt_41_nano.value)
        return result.refusal if result.refusal else result.content


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
