"""Simple test script for weather MCP server tools."""
import asyncio
from main import get_current_weather, get_forecast


async def test():
    print("Testing weather MCP server...\n")

    # Test 1: Get current weather
    print("=" * 50)
    print("Test 1: Get current weather for Seoul")
    print("=" * 50)
    try:
        result = await get_current_weather("Seoul", "KR")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

    print()

    # Test 2: Get forecast
    print("=" * 50)
    print("Test 2: Get 2-day forecast for Seoul")
    print("=" * 50)
    try:
        result = await get_forecast("Seoul", "KR", 2)
        print(result)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test())
