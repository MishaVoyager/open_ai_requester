import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Request

from config.settings import CommonSettings
from domain.models import SearchRequest, SearchResponse
from helpers.open_ai_helper import generate_text, generate_text_async
from helpers.timehelper import measure_time_async

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    if CommonSettings().DRY_MODE:
        await asyncio.sleep(10)
        return SearchResponse(
            answer="Сервер запущен в тестовом режиме. Запросы к OpenAI временно не выполняются",
            is_refusal=False,
            is_success=False
        )
    result = generate_text(request.prompt, model=request.model)
    logging.info(f"Запрос из источника {request.source.value} к модели {request.model}")
    response = SearchResponse(
        answer=result.refusal or result.content,
        is_refusal=result.refusal,
        is_success=True
    )
    return response


answers: dict = dict()


@app.post("/alice")
async def answer_to_alice_user(request: Request) -> dict:
    request_data = await request.json()
    logging.info(str(request_data))
    response = get_response_template(request_data)
    if not request_data['request']['original_utterance']:
        response["response"]["text"] = "Я отвечу при помощи OpenAI. Спрашивайте!"
        return response
    question = request_data['request']['original_utterance']
    user_id = request_data["session"]["user_id"]
    if "ответ" not in question:
        answer = "Отправила ваш запрос в OpenAI. Ответ занимает некоторое время, поскольку система неспешная. Зато " \
                 "получается качественный результат. Ну вот, теперь можешь сказать: скажи ответ"
        response["response"]["text"] = answer
        asyncio.create_task(ask(question, user_id))
    else:
        if user_id not in answers:
            response["response"]["text"] = "Ответ еще не готов"
        else:
            response["response"]["text"] = f"{answers[user_id]}"
            del answers[user_id]
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
async def ask(question: str, user_id: str) -> None:
    if CommonSettings().DRY_MODE:
        await asyncio.sleep(10)
        answers[user_id] = "Ответик пришел"
    else:
        result = await generate_text_async(question)
        answers[user_id] = result.refusal or result.content


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    uvicorn.run(app, host="0.0.0.0", port=7999)
