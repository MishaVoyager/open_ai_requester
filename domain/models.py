from enum import Enum

from pydantic import BaseModel


class Source(Enum):
    YANDEX = 1


class SearchRequest(BaseModel):
    prompt: str
    source: Enum
    model: str = "gpt-4o-mini"


class SearchResponse(BaseModel):
    answer: str
    is_refusal: bool
    is_success: bool
