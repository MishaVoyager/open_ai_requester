import pytest

from config.settings import CommonSettings
from helpers.open_ai_helper import (
    ALICE_MODEL,
    GPTModel,
    generate_alice_reply_async,
    get_async_client,
)


def test_chat_latest_in_model_list() -> None:
    assert GPTModel.gpt_55_instant.value == "chat-latest"
    assert "chat-latest" in [model.value for model in GPTModel]


def test_alice_default_model_is_chat_latest() -> None:
    assert ALICE_MODEL == GPTModel.gpt_55_instant.value


@pytest.mark.skipif(
    CommonSettings().DRY_MODE,
    reason="OpenAI requests are disabled in DRY_MODE",
)
async def test_chat_latest_completion() -> None:
    completion = await get_async_client().chat.completions.create(
        model=GPTModel.gpt_55_instant.value,
        messages=[
            {"role": "system", "content": "Отвечай одним коротким предложением."},
            {"role": "user", "content": "Сколько будет 2+2?"},
        ],
        max_completion_tokens=50,
    )

    assert completion.model
    assert completion.choices[0].message.content
    assert completion.usage is not None
    assert completion.usage.total_tokens > 0


@pytest.mark.skipif(
    CommonSettings().DRY_MODE,
    reason="OpenAI requests are disabled in DRY_MODE",
)
async def test_alice_reply_with_chat_latest() -> None:
    result = await generate_alice_reply_async("Привет! Как дела?")

    assert result.content or result.refusal
