"""Stock ticker analysis tool implementation."""

import logging
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..services.yahoo_finance import YahooFinanceService
from ..utils.errors import ToolError, InvalidSymbolError, APIError

logger = logging.getLogger("investment-helper.tools.ticker_analysis")


class TickerInput(BaseModel):
    """Input schema for analyze_ticker tool."""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Stock ticker symbol (e.g., NVDA, AAPL, TSLA)",
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and normalize the stock symbol."""
        v = v.upper().strip()
        # Allow alphanumeric, ^, . (for indices and special symbols)
        import re
        if not re.match(r"^[A-Z0-9^.]+$", v):
            raise ValueError(
                "Symbol must contain only letters, numbers, ^ or . characters"
            )
        return v


async def analyze_ticker(symbol: str) -> dict[str, Any]:
    """
    Get detailed analysis of a stock ticker.

    Args:
        symbol: Stock ticker symbol (e.g., NVDA, AAPL, TSLA)

    Returns:
        Dictionary containing comprehensive stock analysis.
    """
    logger.info(f"Analyzing ticker: {symbol}")

    # Validate input
    try:
        validated = TickerInput(symbol=symbol)
        symbol = validated.symbol
    except ValueError as e:
        return ToolError(
            message=f"Invalid symbol: {e}",
            suggestion="Use uppercase stock symbols like NVDA, AAPL, TSLA",
        ).to_dict()

    try:
        yahoo_service = YahooFinanceService()
        analysis = await yahoo_service.analyze_ticker(symbol)

        # Format the response
        result = {
            "symbol": analysis["symbol"],
            "name": analysis["name"],
            "current_price": f"${analysis['current_price']:,.2f}"
            if analysis.get("current_price")
            else "N/A",
            "price_raw": analysis.get("current_price"),
            "change": {
                "amount": analysis.get("change"),
                "percent": analysis.get("change_percent"),
                "direction": "up" if (analysis.get("change_percent") or 0) >= 0 else "down",
            },
            "day_range": analysis.get("day_range"),
            "52_week_range": analysis.get("52_week_range"),
            "volume": {
                "current": f"{analysis.get('volume', 0):,}" if analysis.get("volume") else "N/A",
                "average": f"{analysis.get('average_volume', 0):,}"
                if analysis.get("average_volume")
                else "N/A",
                "vs_average": _calculate_volume_ratio(
                    analysis.get("volume"), analysis.get("average_volume")
                ),
            },
            "market_cap": analysis.get("market_cap"),
            "valuation": {
                "pe_ratio": round(analysis.get("pe_ratio", 0), 2)
                if analysis.get("pe_ratio")
                else "N/A",
                "forward_pe": round(analysis.get("forward_pe", 0), 2)
                if analysis.get("forward_pe")
                else "N/A",
            },
            "sector": analysis.get("sector"),
            "industry": analysis.get("industry"),
            "description": analysis.get("description"),
            "trend_analysis": {
                "5_day_trend": analysis.get("5_day_trend"),
                "trend_description": _get_trend_description(analysis.get("5_day_trend")),
            },
            "recent_prices": analysis.get("recent_prices"),
            "market_status": analysis.get("market_status"),
        }

        # Add investment highlights
        result["highlights"] = _generate_highlights(analysis)

        return result

    except InvalidSymbolError as e:
        logger.warning(f"Invalid symbol: {symbol}")
        return ToolError(
            message=f"Stock symbol '{symbol}' not found",
            suggestion="Check the symbol spelling. Common symbols: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA",
        ).to_dict()

    except APIError as e:
        logger.error(f"API error analyzing {symbol}: {e}")
        return ToolError(
            message=f"Error fetching data for {symbol}: {e.message}",
            suggestion="Try again in a few moments. The market data service may be temporarily unavailable.",
        ).to_dict()

    except Exception as e:
        logger.error(f"Unexpected error analyzing {symbol}: {e}", exc_info=True)
        return ToolError(
            message=f"Unexpected error analyzing {symbol}",
            suggestion="Please try again or use a different stock symbol.",
        ).to_dict()


def _calculate_volume_ratio(current: int | None, average: int | None) -> str:
    """Calculate how current volume compares to average."""
    if not current or not average or average == 0:
        return "N/A"

    ratio = current / average
    if ratio > 1.5:
        return f"High ({ratio:.1f}x average)"
    elif ratio > 1.1:
        return f"Above average ({ratio:.1f}x)"
    elif ratio < 0.5:
        return f"Low ({ratio:.1f}x average)"
    elif ratio < 0.9:
        return f"Below average ({ratio:.1f}x)"
    else:
        return "Normal"


def _get_trend_description(trend: str | None) -> str:
    """Get a human-readable description of the trend."""
    descriptions = {
        "strongly_bullish": "Strong upward momentum over the past 5 days",
        "bullish": "Positive trend over the past 5 days",
        "neutral": "Relatively flat price movement over the past 5 days",
        "bearish": "Negative trend over the past 5 days",
        "strongly_bearish": "Strong downward momentum over the past 5 days",
        "insufficient_data": "Not enough data to determine trend",
    }
    return descriptions.get(trend or "", "Unknown trend")


def _generate_highlights(analysis: dict[str, Any]) -> list[str]:
    """Generate key investment highlights from the analysis."""
    highlights = []

    # Price vs 52-week range
    current = analysis.get("current_price")
    week_52 = analysis.get("52_week_range", {})
    if current and week_52.get("low") and week_52.get("high"):
        low, high = week_52["low"], week_52["high"]
        range_position = (current - low) / (high - low) * 100 if high != low else 50
        if range_position > 90:
            highlights.append("Trading near 52-week high")
        elif range_position < 10:
            highlights.append("Trading near 52-week low")
        elif range_position > 70:
            highlights.append("Trading in upper range of 52-week prices")
        elif range_position < 30:
            highlights.append("Trading in lower range of 52-week prices")

    # Volume analysis
    volume = analysis.get("volume")
    avg_volume = analysis.get("average_volume")
    if volume and avg_volume and avg_volume > 0:
        ratio = volume / avg_volume
        if ratio > 2:
            highlights.append("Unusually high trading volume today")
        elif ratio < 0.5:
            highlights.append("Below average trading volume today")

    # P/E analysis
    pe = analysis.get("pe_ratio")
    if pe:
        if pe > 50:
            highlights.append("High P/E ratio suggests growth expectations or overvaluation")
        elif pe < 10:
            highlights.append("Low P/E ratio may indicate value opportunity or concerns")
        elif pe < 0:
            highlights.append("Negative P/E indicates the company is not profitable")

    # Trend
    trend = analysis.get("5_day_trend")
    if trend in ["strongly_bullish", "strongly_bearish"]:
        direction = "upward" if "bullish" in trend else "downward"
        highlights.append(f"Strong {direction} price momentum recently")

    return highlights if highlights else ["No significant highlights detected"]
