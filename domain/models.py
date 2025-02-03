from enum import Enum, StrEnum

from pydantic import BaseModel


class Source(StrEnum):
    YANDEX = "YANDEX"


class SearchRequest(BaseModel):
    prompt: str
    source: Source
    model: str = "gpt-4o-mini"


class SearchResponse(BaseModel):
    answer: str
    is_refusal: bool
    is_success: bool
