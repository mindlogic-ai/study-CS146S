"""설정 및 모델 레지스트리."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

# ── API 설정 ──────────────────────────────────────────────────────────
FACTCHAT_BASE_URL = "https://factchat-cloud.mindlogic.ai"
FACTCHAT_API_KEY = os.getenv("FACTCHAT_API_KEY", "")

ANTHROPIC_ENDPOINT = f"{FACTCHAT_BASE_URL}/v1/api/anthropic/messages"
OPENAI_ENDPOINT = f"{FACTCHAT_BASE_URL}/v1/api/openai/chat/completions"

DEFAULT_MAX_TOKENS = 1024
REQUEST_TIMEOUT = 60.0  # 초


class Provider(str, Enum):
    """LLM 제공사."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass(frozen=True)
class ModelInfo:
    """모델 메타데이터."""

    id: str
    provider: Provider
    display_name: str
    description: str


# ── 모델 레지스트리 ──────────────────────────────────────────────────
AVAILABLE_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="claude-sonnet-4-5-20250929",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4.5",
        description="Anthropic의 균형 잡힌 성능의 중급 모델",
    ),
    ModelInfo(
        id="claude-opus-4-5-20251101",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4.5",
        description="Anthropic의 최고 성능 플래그십 모델",
    ),
    ModelInfo(
        id="claude-haiku-4-5-20251001",
        provider=Provider.ANTHROPIC,
        display_name="Claude Haiku 4.5",
        description="Anthropic의 빠르고 경제적인 경량 모델",
    ),
    ModelInfo(
        id="gpt-5.1-chat-latest",
        provider=Provider.OPENAI,
        display_name="GPT-5.1",
        description="OpenAI의 최신 고성능 모델",
    ),
    ModelInfo(
        id="gpt-5",
        provider=Provider.OPENAI,
        display_name="GPT-5",
        description="OpenAI의 범용 플래그십 모델",
    ),
    ModelInfo(
        id="gpt-5-mini",
        provider=Provider.OPENAI,
        display_name="GPT-5 Mini",
        description="OpenAI의 경량 고속 모델",
    ),
]

MODEL_REGISTRY: dict[str, ModelInfo] = {m.id: m for m in AVAILABLE_MODELS}
