import os
import httpx
import logging
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Configure logging (stderr only for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("weather-mcp")

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Initialize MCP server
mcp = FastMCP("weather-server")


async def make_api_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """Make a request to OpenWeatherMap API with error handling."""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is not set")

    params["appid"] = OPENWEATHER_API_KEY
    params["units"] = "metric"  # Use Celsius

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{OPENWEATHER_BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout while requesting {endpoint}")
            raise ValueError("API request timed out. Please try again.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 404:
                raise ValueError("City not found")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded. Please wait and try again.")
            else:
                raise ValueError(f"API error: {e.response.status_code}")


@mcp.tool()
async def get_current_weather(city: str, country_code: str = "") -> str:
    """
    Get the current weather for a city.

    Args:
        city: Name of the city (e.g., "Seoul", "New York")
        country_code: Optional ISO 3166 country code (e.g., "KR", "US")

    Returns:
        Current weather information including temperature, humidity, and conditions.
    """
    logger.info(f"Getting current weather for {city}")

    query = f"{city},{country_code}" if country_code else city
    data = await make_api_request("weather", {"q": query})

    weather = data["weather"][0]
    main = data["main"]
    wind = data["wind"]

    result = f"""
Current Weather for {data['name']}, {data['sys']['country']}:
- Condition: {weather['main']} ({weather['description']})
- Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)
- Humidity: {main['humidity']}%
- Wind: {wind['speed']} m/s
- Pressure: {main['pressure']} hPa
"""
    return result.strip()


@mcp.tool()
async def get_forecast(city: str, country_code: str = "", days: int = 3) -> str:
    """
    Get weather forecast for a city.

    Args:
        city: Name of the city (e.g., "Seoul", "New York")
        country_code: Optional ISO 3166 country code (e.g., "KR", "US")
        days: Number of days to forecast (1-5, default 3)

    Returns:
        Weather forecast for the specified number of days.
    """
    logger.info(f"Getting {days}-day forecast for {city}")

    if days < 1 or days > 5:
        raise ValueError("Days must be between 1 and 5")

    query = f"{city},{country_code}" if country_code else city
    data = await make_api_request("forecast", {"q": query})

    # Group forecasts by day (API returns 3-hour intervals)
    forecasts_per_day = 8  # 24 hours / 3 hours = 8
    forecasts = data["list"][: days * forecasts_per_day]

    result_lines = [f"Weather Forecast for {data['city']['name']}, {data['city']['country']}:\n"]

    current_date = ""
    for item in forecasts:
        date = item["dt_txt"].split(" ")[0]
        time = item["dt_txt"].split(" ")[1][:5]

        if date != current_date:
            current_date = date
            result_lines.append(f"\n📅 {date}")

        weather = item["weather"][0]
        temp = item["main"]["temp"]
        result_lines.append(f"  {time} - {temp}°C, {weather['description']}")

    return "\n".join(result_lines)


if __name__ == "__main__":
    mcp.run()
