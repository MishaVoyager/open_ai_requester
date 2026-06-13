import logging
from enum import StrEnum
from typing import BinaryIO, Dict, Optional

from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionMessage

from config.settings import CommonSettings

token = CommonSettings().OPENAI_API_KEY

_client: Optional[OpenAI] = None
_async_client: Optional[AsyncOpenAI] = None


async def generate_text_async(
        content: str,
        model: str = "gpt-4o-mini",
        developer_message: Optional[Dict] = None,
        n: int = 1) -> ChatCompletionMessage:
    messages = [
        {"role": "user", "content": f"{content}"}
    ]
    if developer_message:
        messages.append(developer_message)
    completion = await get_async_client().chat.completions.create(
        model=model,
        store=True,
        messages=messages,  # type: ignore
        n=n
    )
    logging.info(f"Запрос к {completion.model} использовал {completion.usage.total_tokens} токенов")
    return completion.choices[0].message


def generate_text(
        content: str,
        model: str = "gpt-4o-mini",
        developer_message: Optional[Dict] = None,
        n: int = 1) -> ChatCompletionMessage:
    messages = [
        {"role": "user", "content": f"{content}"}
    ]
    if developer_message:
        messages.append(developer_message)
    completion = get_client().chat.completions.create(
        model=model,
        store=True,
        messages=messages,  # type: ignore
        n=n
    )
    logging.info(f"Запрос к {completion.model} использовал {completion.usage.total_tokens} токенов")
    return completion.choices[0].message


def audio_to_text(audio_file: BinaryIO) -> str:
    transcription = get_client().audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    return transcription


def text_to_audio(text: str, response_format: str = "mp3") -> BinaryIO:
    response = get_client().audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format=response_format  # type: ignore
    )
    return response.read()  # type: ignore


def generate_image(prompt: str, model: str = "dall-e-3", size: str = "1792x1024") -> Optional[str]:
    response = get_client().images.generate(
        model=model,
        prompt=prompt,
        size=size,  # type: ignore
        quality="standard",
        n=1,
        response_format="b64_json",
        style="natural"
    )
    return response.data[0].b64_json


def get_answer_from_friend(content: str, model: str = "gpt-4o-mini") -> ChatCompletionMessage:
    prompt = """You are an american man. We are friends. We are in a friendly dialogue."""
    developer_message = {"role": "system", "content": prompt}
    return generate_text(content, model, developer_message)


def get_english_teacher_comment(content: str, model: str = "gpt-4o-mini") -> ChatCompletionMessage:
    prompt = """You are a helpful english teacher. 
    Please help to improve grammar, vocabulary and naturalness of this speech.
    Make verbose comment about errors in this areas.
    """
    developer_message = {"role": "system", "content": prompt}
    return generate_text(content, model, developer_message)


def improve_transcript_by_gpt(transcript: str) -> str:
    system_prompt = """
    You are a helpful assistant. Your task is to correct any spelling discrepancies in the transcribed text.
    Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided.
    """

    completion = get_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": transcript
            }
        ]
    )
    return completion.choices[0].message.content


class GPTModel(StrEnum):
    gpt_4o_mini = "gpt-4o-mini"
    gpt_41_nano = "gpt-4.1-nano"
    gpt_54_nano = "gpt-5.4-nano"
    gpt_54_mini = "gpt-5.4-mini"
    gpt_55_instant = "chat-latest"


ALICE_MODEL = GPTModel.gpt_55_instant.value
ALICE_SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "Ты голосовой помощник Яндекс.Алисы. "
        "Отвечай кратко: одно или два коротких предложения, простым разговорным языком."
    ),
}

ALICE_MAX_HISTORY_TURNS = 10
# chat-latest spends part of the budget on reasoning tokens; 120 is not enough for content.
ALICE_MAX_COMPLETION_TOKENS = 300


async def generate_alice_reply_async(
    question: str,
    history: Optional[list] = None,
) -> ChatCompletionMessage:
    messages = [ALICE_SYSTEM_MESSAGE]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})
    completion = await get_async_client().chat.completions.create(
        model=ALICE_MODEL,
        store=False,
        max_completion_tokens=ALICE_MAX_COMPLETION_TOKENS,
        messages=messages,  # type: ignore
    )
    logging.info(
        f"Запрос Алисы к {completion.model} использовал {completion.usage.total_tokens} токенов"
    )
    return completion.choices[0].message


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=token,
            organization="org-ivGGIRGxUk5rZmvxkoypdUUy",
            project="proj_t7kgt6Awz7m2knmH4gL0xeh2"
        )
    return _client


def get_async_client() -> AsyncOpenAI:
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(
            api_key=token,
            organization="org-ivGGIRGxUk5rZmvxkoypdUUy",
            project="proj_t7kgt6Awz7m2knmH4gL0xeh2"
        )
    return _async_client
