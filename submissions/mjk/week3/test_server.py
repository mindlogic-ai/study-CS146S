"""간단한 서버 테스트 스크립트."""

import asyncio
import json

from server.config import AVAILABLE_MODELS, MODEL_REGISTRY
from server.main import compare_models, list_models


async def test_list_models():
    """list_models 도구 테스트."""
    print("=== Testing list_models ===")
    result = await list_models()
    data = json.loads(result)
    print(f"Total models: {data['total']}")
    for model in data["models"]:
        print(f"  - {model['display_name']} ({model['model_id']})")
    assert data["total"] == 6
    print("✓ list_models test passed\n")


async def test_compare_models_validation():
    """compare_models 입력 유효성 검사 테스트."""
    print("=== Testing compare_models validation ===")

    # 빈 프롬프트
    result = await compare_models(prompt="", model_ids=None)
    data = json.loads(result)
    assert "error" in data
    print(f"✓ Empty prompt error: {data['error']}")

    # 유효하지 않은 모델 ID
    result = await compare_models(prompt="test", model_ids=["invalid-model"])
    data = json.loads(result)
    assert "error" in data
    print(f"✓ Invalid model ID error: {data['error'][:50]}...")

    print("✓ Validation tests passed\n")


async def test_config():
    """설정 테스트."""
    print("=== Testing configuration ===")
    print(f"Total models in registry: {len(MODEL_REGISTRY)}")
    print(f"Available models: {len(AVAILABLE_MODELS)}")
    assert len(MODEL_REGISTRY) == 6
    assert len(AVAILABLE_MODELS) == 6

    # 모든 모델이 레지스트리에 있는지 확인
    for model in AVAILABLE_MODELS:
        assert model.id in MODEL_REGISTRY
        print(f"  ✓ {model.display_name} registered")

    print("✓ Configuration tests passed\n")


async def main():
    """모든 테스트 실행."""
    print("Starting MCP Server Tests\n")
    print("=" * 60)

    await test_config()
    await test_list_models()
    await test_compare_models_validation()

    print("=" * 60)
    print("\n✓ All tests passed!")
    print("\nNote: API call tests require FACTCHAT_API_KEY in .env file")


if __name__ == "__main__":
    asyncio.run(main())
