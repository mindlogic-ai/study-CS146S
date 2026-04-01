"""CoinGecko API service for cryptocurrency data."""

import logging
from typing import Any

import httpx

from ..config import settings
from ..utils.errors import InvalidSymbolError, APIError, RateLimitError
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger("investment-helper.coingecko")


class CoinGeckoService:
    """Service for fetching cryptocurrency data from CoinGecko API."""

    def __init__(self):
        self.base_url = settings.coingecko_base_url
        self.timeout = settings.request_timeout
        self.rate_limiter = RateLimiter(settings.coingecko_rate_limit)

    async def _request(self, endpoint: str, params: dict | None = None) -> Any:
        """
        Make a rate-limited request to the CoinGecko API.

        Args:
            endpoint: API endpoint (without base URL).
            params: Optional query parameters.

        Returns:
            JSON response data.

        Raises:
            RateLimitError: If rate limit is exceeded.
            APIError: If the API request fails.
        """
        await self.rate_limiter.acquire()

        url = f"{self.base_url}{endpoint}"
        logger.info(f"CoinGecko request: {endpoint}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    raise RateLimitError(
                        "CoinGecko rate limit exceeded. Please wait before retrying."
                    )

                if response.status_code == 404:
                    raise InvalidSymbolError(
                        endpoint.split("/")[-1], "cryptocurrency"
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise APIError("CoinGecko", message="Request timed out")
        except httpx.HTTPStatusError as e:
            raise APIError("CoinGecko", status_code=e.response.status_code)
        except RateLimitError:
            raise
        except InvalidSymbolError:
            raise
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
            raise APIError("CoinGecko", message=str(e))

    async def get_global_data(self) -> dict[str, Any]:
        """
        Get global cryptocurrency market data.

        Returns:
            Dictionary with global market statistics.
        """
        data = await self._request("/global")
        global_data = data.get("data", {})

        return {
            "total_market_cap_usd": global_data.get("total_market_cap", {}).get("usd"),
            "total_volume_24h_usd": global_data.get("total_volume", {}).get("usd"),
            "bitcoin_dominance": global_data.get("market_cap_percentage", {}).get("btc"),
            "ethereum_dominance": global_data.get("market_cap_percentage", {}).get("eth"),
            "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
            "markets": global_data.get("markets"),
            "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd"),
        }

    async def get_trending(self) -> list[dict[str, Any]]:
        """
        Get trending cryptocurrencies in the last 24 hours.

        Returns:
            List of trending coins.
        """
        data = await self._request("/search/trending")
        coins = data.get("coins", [])

        return [
            {
                "id": coin["item"]["id"],
                "name": coin["item"]["name"],
                "symbol": coin["item"]["symbol"],
                "market_cap_rank": coin["item"].get("market_cap_rank"),
                "score": coin["item"].get("score"),
            }
            for coin in coins[:7]  # Top 7 trending
        ]

    async def get_top_coins(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get top cryptocurrencies by market cap.

        Args:
            limit: Number of coins to return (max 100).

        Returns:
            List of top coins with market data.
        """
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": min(limit, 100),
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
        }

        data = await self._request("/coins/markets", params=params)

        return [
            {
                "id": coin["id"],
                "symbol": coin["symbol"].upper(),
                "name": coin["name"],
                "current_price": coin["current_price"],
                "market_cap": coin["market_cap"],
                "market_cap_rank": coin["market_cap_rank"],
                "price_change_24h": coin.get("price_change_percentage_24h"),
                "price_change_7d": coin.get("price_change_percentage_7d_in_currency"),
                "volume_24h": coin["total_volume"],
            }
            for coin in data
        ]

    async def get_coin_detail(self, coin_id: str) -> dict[str, Any]:
        """
        Get detailed information for a specific cryptocurrency.

        Args:
            coin_id: CoinGecko coin ID (e.g., bitcoin, ethereum, solana)

        Returns:
            Dictionary with comprehensive coin data.

        Raises:
            InvalidSymbolError: If the coin ID is not found.
        """
        coin_id = coin_id.lower().strip()
        logger.info(f"Fetching coin detail for: {coin_id}")

        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "true",
            "developer_data": "false",
            "sparkline": "false",
        }

        data = await self._request(f"/coins/{coin_id}", params=params)

        market_data = data.get("market_data", {})
        community_data = data.get("community_data", {})

        # Get description (first 200 chars)
        description = data.get("description", {}).get("en", "")
        # Remove HTML tags
        import re
        description = re.sub(r"<[^>]+>", "", description)
        if len(description) > 200:
            description = description[:197] + "..."

        # Format market cap
        market_cap = market_data.get("market_cap", {}).get("usd")
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap / 1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap / 1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap / 1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
        else:
            market_cap_str = "N/A"

        return {
            "id": data["id"],
            "symbol": data["symbol"].upper(),
            "name": data["name"],
            "description": description,
            "current_price_usd": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_cap_str,
            "market_cap_raw": market_cap,
            "market_cap_rank": data.get("market_cap_rank"),
            "price_change_24h": market_data.get("price_change_percentage_24h"),
            "price_change_7d": market_data.get("price_change_percentage_7d"),
            "price_change_30d": market_data.get("price_change_percentage_30d"),
            "volume_24h": market_data.get("total_volume", {}).get("usd"),
            "all_time_high": {
                "price": market_data.get("ath", {}).get("usd"),
                "date": market_data.get("ath_date", {}).get("usd"),
                "change_percent": market_data.get("ath_change_percentage", {}).get("usd"),
            },
            "all_time_low": {
                "price": market_data.get("atl", {}).get("usd"),
                "date": market_data.get("atl_date", {}).get("usd"),
                "change_percent": market_data.get("atl_change_percentage", {}).get("usd"),
            },
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "community_sentiment": {
                "up_votes": community_data.get("sentiment_votes_up_percentage"),
                "down_votes": community_data.get("sentiment_votes_down_percentage"),
            },
            "links": {
                "homepage": data.get("links", {}).get("homepage", [None])[0],
                "twitter": data.get("links", {}).get("twitter_screen_name"),
                "subreddit": data.get("links", {}).get("subreddit_url"),
            },
        }

    async def get_btc_eth_summary(self) -> dict[str, Any]:
        """
        Get quick summary of Bitcoin and Ethereum.

        Returns:
            Dictionary with BTC and ETH key metrics.
        """
        coins = await self.get_top_coins(limit=2)

        btc = next((c for c in coins if c["id"] == "bitcoin"), None)
        eth = next((c for c in coins if c["id"] == "ethereum"), None)

        return {
            "bitcoin": {
                "price": btc["current_price"] if btc else None,
                "change_24h": btc["price_change_24h"] if btc else None,
                "market_cap": btc["market_cap"] if btc else None,
            } if btc else {"error": "Data not available"},
            "ethereum": {
                "price": eth["current_price"] if eth else None,
                "change_24h": eth["price_change_24h"] if eth else None,
                "market_cap": eth["market_cap"] if eth else None,
            } if eth else {"error": "Data not available"},
        }
