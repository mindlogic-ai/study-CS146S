"""Cryptocurrency analysis tool implementation."""

import logging
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..services.coingecko import CoinGeckoService
from ..utils.errors import ToolError, InvalidSymbolError, APIError, RateLimitError

logger = logging.getLogger("investment-helper.tools.crypto_analysis")


class CryptoInput(BaseModel):
    """Input schema for get_crypto_analysis tool."""

    coin_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="CoinGecko coin ID (e.g., bitcoin, ethereum, solana). Use lowercase.",
    )

    @field_validator("coin_id")
    @classmethod
    def validate_coin_id(cls, v: str) -> str:
        """Validate and normalize the coin ID."""
        v = v.lower().strip()
        # Allow alphanumeric and hyphens (common in CoinGecko IDs)
        import re
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Coin ID must be lowercase with only letters, numbers, or hyphens"
            )
        return v


async def get_crypto_analysis(coin_id: str) -> dict[str, Any]:
    """
    Get detailed analysis of a cryptocurrency.

    Args:
        coin_id: CoinGecko coin ID (e.g., bitcoin, ethereum, solana)

    Returns:
        Dictionary containing comprehensive cryptocurrency analysis.
    """
    logger.info(f"Analyzing cryptocurrency: {coin_id}")

    # Validate input
    try:
        validated = CryptoInput(coin_id=coin_id)
        coin_id = validated.coin_id
    except ValueError as e:
        return ToolError(
            message=f"Invalid coin ID: {e}",
            suggestion="Use lowercase CoinGecko IDs like 'bitcoin', 'ethereum', 'solana'",
        ).to_dict()

    try:
        coingecko_service = CoinGeckoService()
        coin_data = await coingecko_service.get_coin_detail(coin_id)

        # Format the response
        result = {
            "coin_id": coin_data["id"],
            "symbol": coin_data["symbol"],
            "name": coin_data["name"],
            "description": coin_data.get("description"),
            "current_price": f"${coin_data['current_price_usd']:,.2f}"
            if coin_data.get("current_price_usd")
            else "N/A",
            "price_raw": coin_data.get("current_price_usd"),
            "market_cap": coin_data.get("market_cap"),
            "market_cap_rank": coin_data.get("market_cap_rank"),
            "price_changes": {
                "24h": _format_change(coin_data.get("price_change_24h")),
                "7d": _format_change(coin_data.get("price_change_7d")),
                "30d": _format_change(coin_data.get("price_change_30d")),
            },
            "volume_24h": _format_large_number(coin_data.get("volume_24h")),
            "all_time_high": {
                "price": f"${coin_data['all_time_high']['price']:,.2f}"
                if coin_data.get("all_time_high", {}).get("price")
                else "N/A",
                "date": coin_data.get("all_time_high", {}).get("date", "")[:10]
                if coin_data.get("all_time_high", {}).get("date")
                else "N/A",
                "change_from_ath": f"{coin_data['all_time_high']['change_percent']:.1f}%"
                if coin_data.get("all_time_high", {}).get("change_percent")
                else "N/A",
            },
            "all_time_low": {
                "price": f"${coin_data['all_time_low']['price']:,.6f}"
                if coin_data.get("all_time_low", {}).get("price")
                else "N/A",
                "date": coin_data.get("all_time_low", {}).get("date", "")[:10]
                if coin_data.get("all_time_low", {}).get("date")
                else "N/A",
                "change_from_atl": f"+{coin_data['all_time_low']['change_percent']:,.0f}%"
                if coin_data.get("all_time_low", {}).get("change_percent")
                else "N/A",
            },
            "supply": {
                "circulating": _format_supply(coin_data.get("circulating_supply")),
                "total": _format_supply(coin_data.get("total_supply")),
                "max": _format_supply(coin_data.get("max_supply")),
                "percent_circulating": _calculate_supply_percent(
                    coin_data.get("circulating_supply"),
                    coin_data.get("max_supply") or coin_data.get("total_supply"),
                ),
            },
            "community_sentiment": coin_data.get("community_sentiment"),
            "links": coin_data.get("links"),
        }

        # Add analysis highlights
        result["analysis"] = _generate_crypto_analysis(coin_data)

        return result

    except InvalidSymbolError as e:
        logger.warning(f"Invalid coin ID: {coin_id}")
        return ToolError(
            message=f"Cryptocurrency '{coin_id}' not found on CoinGecko",
            suggestion="Common IDs: bitcoin, ethereum, solana, cardano, dogecoin. "
            "Use the CoinGecko website to find the correct coin ID.",
        ).to_dict()

    except RateLimitError as e:
        logger.warning(f"Rate limited: {e}")
        return ToolError(
            message="CoinGecko API rate limit exceeded",
            suggestion=f"Please wait {e.wait_seconds:.0f} seconds before trying again.",
        ).to_dict()

    except APIError as e:
        logger.error(f"API error analyzing {coin_id}: {e}")
        return ToolError(
            message=f"Error fetching data for {coin_id}: {e.message}",
            suggestion="Try again in a few moments. CoinGecko may be temporarily unavailable.",
        ).to_dict()

    except Exception as e:
        logger.error(f"Unexpected error analyzing {coin_id}: {e}", exc_info=True)
        return ToolError(
            message=f"Unexpected error analyzing {coin_id}",
            suggestion="Please try again or use a different cryptocurrency ID.",
        ).to_dict()


def _format_change(change: float | None) -> dict[str, Any]:
    """Format a price change percentage."""
    if change is None:
        return {"value": "N/A", "direction": "unknown"}

    return {
        "value": f"{change:+.2f}%",
        "raw": round(change, 2),
        "direction": "up" if change >= 0 else "down",
    }


def _format_large_number(value: float | None) -> str:
    """Format a large number for display."""
    if value is None:
        return "N/A"

    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    elif value >= 1e9:
        return f"${value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.2f}M"
    else:
        return f"${value:,.0f}"


def _format_supply(value: float | None) -> str:
    """Format a supply number for display."""
    if value is None:
        return "N/A"

    if value >= 1e12:
        return f"{value / 1e12:.2f}T"
    elif value >= 1e9:
        return f"{value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"{value / 1e6:.2f}M"
    else:
        return f"{value:,.0f}"


def _calculate_supply_percent(circulating: float | None, max_supply: float | None) -> str:
    """Calculate the percentage of supply in circulation."""
    if not circulating or not max_supply or max_supply == 0:
        return "N/A"

    percent = (circulating / max_supply) * 100
    return f"{percent:.1f}%"


def _generate_crypto_analysis(coin_data: dict[str, Any]) -> dict[str, Any]:
    """Generate analysis insights from coin data."""
    insights = []
    signals = {"bullish": [], "bearish": [], "neutral": []}

    # Price momentum analysis
    change_24h = coin_data.get("price_change_24h")
    change_7d = coin_data.get("price_change_7d")
    change_30d = coin_data.get("price_change_30d")

    if change_24h is not None and change_7d is not None:
        if change_24h > 5 and change_7d > 10:
            signals["bullish"].append("Strong short-term momentum")
            insights.append("Price showing strong upward momentum across multiple timeframes")
        elif change_24h < -5 and change_7d < -10:
            signals["bearish"].append("Negative short-term momentum")
            insights.append("Price under pressure with sustained selling")
        elif change_24h > 0 and change_7d < 0:
            insights.append("Recent bounce after weekly decline - potential reversal or dead cat bounce")
        elif change_24h < 0 and change_7d > 0:
            insights.append("Short-term pullback in an uptrend")

    # Distance from ATH
    ath_change = coin_data.get("all_time_high", {}).get("change_percent")
    if ath_change is not None:
        if ath_change > -10:
            signals["bullish"].append("Near all-time high")
            insights.append("Trading near all-time high levels")
        elif ath_change < -80:
            signals["bearish"].append("Far from ATH")
            insights.append(f"Trading {abs(ath_change):.0f}% below all-time high")
        elif ath_change < -50:
            insights.append(f"Significant decline ({abs(ath_change):.0f}%) from ATH - potential value or further downside")

    # Supply analysis
    circulating = coin_data.get("circulating_supply")
    max_supply = coin_data.get("max_supply")
    if circulating and max_supply:
        percent = (circulating / max_supply) * 100
        if percent > 90:
            signals["bullish"].append("High % of supply in circulation")
            insights.append("Most of the maximum supply is already in circulation (limited future dilution)")
        elif percent < 50:
            signals["bearish"].append("Significant future supply inflation possible")
            insights.append(f"Only {percent:.0f}% of max supply in circulation - potential for future dilution")

    # Community sentiment
    sentiment = coin_data.get("community_sentiment", {})
    up_votes = sentiment.get("up_votes")
    if up_votes is not None:
        if up_votes > 70:
            signals["bullish"].append("Strong community sentiment")
        elif up_votes < 40:
            signals["bearish"].append("Weak community sentiment")

    # Market cap rank
    rank = coin_data.get("market_cap_rank")
    if rank:
        if rank <= 10:
            insights.append(f"Top 10 cryptocurrency by market cap (#{rank})")
        elif rank <= 50:
            insights.append(f"Established cryptocurrency (#{rank} by market cap)")
        elif rank > 100:
            insights.append(f"Smaller market cap cryptocurrency (#{rank}) - higher risk/reward")

    # Overall assessment
    bullish_count = len(signals["bullish"])
    bearish_count = len(signals["bearish"])

    if bullish_count > bearish_count + 1:
        overall = "bullish"
    elif bearish_count > bullish_count + 1:
        overall = "bearish"
    else:
        overall = "neutral"

    return {
        "overall_sentiment": overall,
        "bullish_signals": signals["bullish"],
        "bearish_signals": signals["bearish"],
        "insights": insights if insights else ["No significant patterns detected"],
    }
