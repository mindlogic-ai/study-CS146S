"""Market briefing tool implementation."""

import logging
from typing import Any

from pydantic import BaseModel, Field

from ..services.yahoo_finance import YahooFinanceService
from ..services.coingecko import CoinGeckoService
from ..utils.errors import ToolError

logger = logging.getLogger("investment-helper.tools.market_briefing")


class MarketBriefingInput(BaseModel):
    """Input schema for get_market_briefing tool."""

    include_crypto: bool = Field(
        default=True,
        description="Include cryptocurrency summary in the briefing",
    )
    indices: list[str] = Field(
        default=["^GSPC", "^IXIC", "^DJI"],
        description="Index symbols to include (^GSPC=S&P500, ^IXIC=NASDAQ, ^DJI=Dow Jones)",
    )


async def get_market_briefing(
    include_crypto: bool = True,
    indices: list[str] | None = None,
) -> dict[str, Any]:
    """
    Get a morning briefing of stock indices and crypto market overview.

    Args:
        include_crypto: Whether to include cryptocurrency data.
        indices: List of stock index symbols to include.

    Returns:
        Dictionary containing market briefing data.
    """
    logger.info(f"Generating market briefing (crypto={include_crypto})")

    if indices is None:
        indices = ["^GSPC", "^IXIC", "^DJI"]

    result: dict[str, Any] = {
        "briefing_type": "market_overview",
    }

    # Get stock market data
    try:
        yahoo_service = YahooFinanceService()
        market_status = yahoo_service.is_market_open()
        indices_data = await yahoo_service.get_multiple_indices(indices)

        # Format indices for display
        formatted_indices = []
        for idx in indices_data:
            if "error" in idx:
                formatted_indices.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "error": idx["error"],
                })
            else:
                change_pct = idx.get("change_percent", 0)
                direction = "up" if change_pct >= 0 else "down"
                formatted_indices.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "price": idx.get("price"),
                    "change": round(idx.get("change", 0), 2),
                    "change_percent": round(change_pct, 2),
                    "direction": direction,
                    "day_range": f"{idx.get('day_low'):.2f} - {idx.get('day_high'):.2f}"
                    if idx.get("day_low") and idx.get("day_high")
                    else None,
                })

        result["market_status"] = market_status
        result["indices"] = formatted_indices

    except Exception as e:
        logger.error(f"Error fetching stock market data: {e}")
        result["indices_error"] = str(e)

    # Get crypto market data if requested
    if include_crypto:
        try:
            coingecko_service = CoinGeckoService()

            # Get global crypto data
            global_data = await coingecko_service.get_global_data()

            # Format market cap
            total_mcap = global_data.get("total_market_cap_usd")
            if total_mcap:
                if total_mcap >= 1e12:
                    mcap_str = f"${total_mcap / 1e12:.2f}T"
                else:
                    mcap_str = f"${total_mcap / 1e9:.2f}B"
            else:
                mcap_str = "N/A"

            result["crypto_global"] = {
                "total_market_cap": mcap_str,
                "market_cap_change_24h": round(
                    global_data.get("market_cap_change_24h", 0), 2
                ),
                "bitcoin_dominance": round(
                    global_data.get("bitcoin_dominance", 0), 1
                ),
                "ethereum_dominance": round(
                    global_data.get("ethereum_dominance", 0), 1
                ),
                "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
            }

            # Get BTC and ETH summary
            btc_eth = await coingecko_service.get_btc_eth_summary()
            result["major_crypto"] = {
                "bitcoin": {
                    "price": f"${btc_eth['bitcoin']['price']:,.2f}"
                    if btc_eth.get("bitcoin", {}).get("price")
                    else "N/A",
                    "change_24h": round(
                        btc_eth.get("bitcoin", {}).get("change_24h", 0) or 0, 2
                    ),
                },
                "ethereum": {
                    "price": f"${btc_eth['ethereum']['price']:,.2f}"
                    if btc_eth.get("ethereum", {}).get("price")
                    else "N/A",
                    "change_24h": round(
                        btc_eth.get("ethereum", {}).get("change_24h", 0) or 0, 2
                    ),
                },
            }

            # Get trending coins
            trending = await coingecko_service.get_trending()
            result["trending_crypto"] = [
                {
                    "name": coin["name"],
                    "symbol": coin["symbol"],
                    "rank": coin.get("market_cap_rank"),
                }
                for coin in trending[:5]
            ]

        except Exception as e:
            logger.error(f"Error fetching crypto market data: {e}")
            result["crypto_error"] = str(e)

    # Generate summary text
    summary_parts = []

    if "indices" in result:
        for idx in result["indices"]:
            if "error" not in idx:
                arrow = "▲" if idx["direction"] == "up" else "▼"
                summary_parts.append(
                    f"{idx['name']}: {idx.get('price', 'N/A'):,.2f} "
                    f"({arrow} {abs(idx['change_percent']):.2f}%)"
                )

    if include_crypto and "major_crypto" in result:
        btc = result["major_crypto"]["bitcoin"]
        eth = result["major_crypto"]["ethereum"]
        btc_arrow = "▲" if btc.get("change_24h", 0) >= 0 else "▼"
        eth_arrow = "▲" if eth.get("change_24h", 0) >= 0 else "▼"
        summary_parts.append(
            f"BTC: {btc['price']} ({btc_arrow} {abs(btc.get('change_24h', 0)):.2f}%)"
        )
        summary_parts.append(
            f"ETH: {eth['price']} ({eth_arrow} {abs(eth.get('change_24h', 0)):.2f}%)"
        )

    result["summary"] = " | ".join(summary_parts)

    return result
