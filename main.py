import logging

import asyncio
from fastapi import FastAPI

from config.settings import CommonSettings
from domain.models import SearchRequest, SearchResponse
from helpers.open_ai_helper import generate_text

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/search", response_model=SearchResponse)
async def read_item(request: SearchRequest) -> SearchResponse:
    if CommonSettings().DRY_MODE:
        await asyncio.sleep(10000)
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
