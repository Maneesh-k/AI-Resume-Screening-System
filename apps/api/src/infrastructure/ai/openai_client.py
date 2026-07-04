from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import structlog
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def chat_completion(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = True,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    """Call OpenAI chat completion with retry. Returns parsed JSON dict."""
    client = get_openai_client()

    response = await client.chat.completions.create(
        model=settings.openai_llm_model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"} if json_mode else {"type": "text"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or "{}"
    log.info(
        "llm_call_complete",
        model=settings.openai_llm_model,
        prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
        completion_tokens=response.usage.completion_tokens if response.usage else 0,
    )

    if json_mode:
        return json.loads(content)  # type: ignore[no-any-return]
    return {"content": content}


async def chat_completion_stream(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    """Streaming chat completion. Yields text chunks."""
    client = get_openai_client()

    stream = await client.chat.completions.create(
        model=settings.openai_llm_model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using text-embedding-3-large."""
    client = get_openai_client()

    # Truncate to avoid token limit (8191 tokens for this model)
    text = text[:30000]

    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
        dimensions=settings.openai_embedding_dimensions,
    )

    return response.data[0].embedding
