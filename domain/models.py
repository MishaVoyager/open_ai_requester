from enum import Enum, StrEnum

from pydantic import BaseModel


class Source(StrEnum):
    YANDEX = "YANDEX"
    OTHER = "OTHER"


class SearchRequest(BaseModel):
    prompt: str
    source: Source = Source.OTHER
    model: str = "gpt-4o-mini"


class SearchResponse(BaseModel):
    answer: str
    is_refusal: bool
    is_success: bool
