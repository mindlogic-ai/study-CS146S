"""API 호출 및 에러 처리."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import httpx

from server.config import (
    ANTHROPIC_ENDPOINT,
    DEFAULT_MAX_TOKENS,
    FACTCHAT_API_KEY,
    MODEL_REGISTRY,
    OPENAI_ENDPOINT,
    REQUEST_TIMEOUT,
    ModelInfo,
    Provider,
)


@dataclass
class ModelResponse:
    """개별 모델의 응답 결과."""

    model_id: str
    display_name: str
    provider: str
    content: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None


async def call_anthropic(
    client: httpx.AsyncClient,
    model_id: str,
    prompt: str,
    max_tokens: int,
) -> dict:
    """Anthropic Messages API 호출."""
    headers = {
        "Authorization": f"Bearer {FACTCHAT_API_KEY}",
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = await client.post(ANTHROPIC_ENDPOINT, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


async def call_openai(
    client: httpx.AsyncClient,
    model_id: str,
    prompt: str,
) -> dict:
    """OpenAI Chat Completions API 호출."""
    headers = {
        "Authorization": f"Bearer {FACTCHAT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = await client.post(OPENAI_ENDPOINT, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


def parse_anthropic_response(data: dict) -> tuple[str, int | None, int | None]:
    """Anthropic 응답에서 텍스트와 토큰 사용량 추출."""
    content_blocks = data.get("content", [])
    text_parts = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
    content = "\n".join(text_parts) if text_parts else "(응답 없음)"
    usage = data.get("usage", {})
    return content, usage.get("input_tokens"), usage.get("output_tokens")


def parse_openai_response(data: dict) -> tuple[str, int | None, int | None]:
    """OpenAI 응답에서 텍스트와 토큰 사용량 추출."""
    choices = data.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "(응답 없음)")
    else:
        content = "(응답 없음)"
    usage = data.get("usage", {})
    return content, usage.get("prompt_tokens"), usage.get("completion_tokens")


async def query_model(
    client: httpx.AsyncClient,
    model_id: str,
    prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> ModelResponse:
    """단일 모델에 프롬프트를 보내고 ModelResponse 반환."""
    info: ModelInfo = MODEL_REGISTRY[model_id]
    start = time.monotonic()
    try:
        if info.provider == Provider.ANTHROPIC:
            raw = await call_anthropic(client, model_id, prompt, max_tokens)
            content, in_tok, out_tok = parse_anthropic_response(raw)
        else:
            raw = await call_openai(client, model_id, prompt)
            content, in_tok, out_tok = parse_openai_response(raw)

        elapsed = (time.monotonic() - start) * 1000
        return ModelResponse(
            model_id=model_id,
            display_name=info.display_name,
            provider=info.provider.value,
            content=content,
            latency_ms=round(elapsed, 1),
            input_tokens=in_tok,
            output_tokens=out_tok,
        )
    except httpx.TimeoutException:
        elapsed = (time.monotonic() - start) * 1000
        return ModelResponse(
            model_id=model_id,
            display_name=info.display_name,
            provider=info.provider.value,
            content="",
            latency_ms=round(elapsed, 1),
            error=f"타임아웃 ({REQUEST_TIMEOUT}초 초과)",
        )
    except httpx.HTTPStatusError as exc:
        elapsed = (time.monotonic() - start) * 1000
        status = exc.response.status_code
        detail = f"HTTP {status}"
        if status == 429:
            detail = "Rate limit 초과 - 잠시 후 다시 시도하세요"
        elif status == 401:
            detail = "인증 실패 - API 키를 확인하세요"
        elif status >= 500:
            detail = f"서버 오류 (HTTP {status})"
        return ModelResponse(
            model_id=model_id,
            display_name=info.display_name,
            provider=info.provider.value,
            content="",
            latency_ms=round(elapsed, 1),
            error=detail,
        )
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return ModelResponse(
            model_id=model_id,
            display_name=info.display_name,
            provider=info.provider.value,
            content="",
            latency_ms=round(elapsed, 1),
            error=f"예기치 않은 오류: {type(exc).__name__}: {exc}",
        )


async def query_models(
    model_ids: list[str],
    prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> list[ModelResponse]:
    """여러 모델에 동시에 프롬프트를 보내고 결과 반환."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        tasks = [query_model(client, model_id, prompt, max_tokens) for model_id in model_ids]
        return await asyncio.gather(*tasks)
