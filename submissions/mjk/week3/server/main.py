"""FastMCP 서버 진입점."""

from __future__ import annotations

import json
import logging

from mcp.server.fastmcp import FastMCP

from server.client import query_models
from server.config import AVAILABLE_MODELS, FACTCHAT_API_KEY, MODEL_REGISTRY

# ── 로깅 설정 (STDIO 모드에서는 stderr로만 출력) ──────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastMCP 서버 생성 ──────────────────────────────────────────────
mcp = FastMCP(
    name="factchat-compare",
    instructions=(
        "FactChat 다중 LLM 비교 서버입니다. "
        "동일한 프롬프트를 여러 AI 모델에 동시에 보내고 응답을 비교할 수 있습니다."
    ),
)


# ── Tool 1: list_models ───────────────────────────────────────────
@mcp.tool(
    name="list_models",
    description=(
        "사용 가능한 모든 LLM 모델 목록을 반환합니다. "
        "각 모델의 ID, 제공사(provider), 표시 이름, 설명을 포함합니다."
    ),
)
async def list_models() -> str:
    """사용 가능한 모델 목록을 JSON 형식으로 반환."""
    models = [
        {
            "model_id": m.id,
            "provider": m.provider.value,
            "display_name": m.display_name,
            "description": m.description,
        }
        for m in AVAILABLE_MODELS
    ]
    return json.dumps(
        {"total": len(models), "models": models},
        ensure_ascii=False,
        indent=2,
    )


# ── Tool 2: compare_models ────────────────────────────────────────
@mcp.tool(
    name="compare_models",
    description=(
        "동일한 프롬프트를 선택한 LLM 모델들에 동시에 보내고, "
        "각 모델의 응답/지연 시간/토큰 사용량을 비교 형식으로 반환합니다. "
        "model_ids를 비워두면 전체 모델에 보냅니다."
    ),
)
async def compare_models(
    prompt: str,
    model_ids: list[str] | None = None,
    max_tokens: int = 1024,
) -> str:
    """여러 모델의 응답을 비교."""
    # API 키 확인
    if not FACTCHAT_API_KEY:
        return json.dumps(
            {"error": "FACTCHAT_API_KEY 환경 변수가 설정되지 않았습니다."},
            ensure_ascii=False,
        )

    # 모델 ID 유효성 검사
    if model_ids:
        invalid = [mid for mid in model_ids if mid not in MODEL_REGISTRY]
        if invalid:
            return json.dumps(
                {
                    "error": f"유효하지 않은 모델 ID: {invalid}",
                    "available_models": list(MODEL_REGISTRY.keys()),
                },
                ensure_ascii=False,
                indent=2,
            )
        target_ids = model_ids
    else:
        target_ids = list(MODEL_REGISTRY.keys())

    if not prompt.strip():
        return json.dumps(
            {"error": "프롬프트가 비어있습니다."},
            ensure_ascii=False,
        )

    logger.info(
        "비교 요청: %d개 모델, 프롬프트: %.50s...",
        len(target_ids),
        prompt,
    )

    responses = await query_models(target_ids, prompt, max_tokens)

    # 결과 포맷팅
    results = []
    for r in responses:
        entry = {
            "model_id": r.model_id,
            "display_name": r.display_name,
            "provider": r.provider,
            "latency_ms": r.latency_ms,
        }
        if r.error:
            entry["status"] = "error"
            entry["error"] = r.error
        else:
            entry["status"] = "success"
            entry["content"] = r.content
            if r.input_tokens is not None:
                entry["input_tokens"] = r.input_tokens
            if r.output_tokens is not None:
                entry["output_tokens"] = r.output_tokens
        results.append(entry)

    # 응답 시간 순 정렬 (빠른 순)
    results.sort(key=lambda x: x["latency_ms"])

    output = {
        "prompt": prompt,
        "models_queried": len(results),
        "successful": sum(1 for r in results if r.get("status") == "success"),
        "failed": sum(1 for r in results if r.get("status") == "error"),
        "results": results,
    }

    return json.dumps(output, ensure_ascii=False, indent=2)


# ── 진입점 ────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
