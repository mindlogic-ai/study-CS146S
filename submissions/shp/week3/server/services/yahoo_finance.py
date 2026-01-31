"""Yahoo Finance service wrapper using yfinance library."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

from ..utils.errors import InvalidSymbolError, APIError

logger = logging.getLogger("investment-helper.yahoo")


class YahooFinanceService:
    """Service for fetching stock data via yfinance."""

    # Default indices for market briefing
    DEFAULT_INDICES = ["^GSPC", "^IXIC", "^DJI"]
    INDEX_NAMES = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ Composite",
        "^DJI": "Dow Jones Industrial",
        "^RUT": "Russell 2000",
        "^VIX": "VIX (Volatility)",
    }

    async def get_ticker_info(self, symbol: str) -> dict[str, Any]:
        """
        Get detailed information for a stock ticker.

        Args:
            symbol: Stock ticker symbol (e.g., NVDA, AAPL, TSLA)

        Returns:
            Dictionary containing stock information.

        Raises:
            InvalidSymbolError: If the symbol is invalid or not found.
            APIError: If there's an error fetching data.
        """
        logger.info(f"Fetching ticker info for: {symbol}")
        symbol = symbol.upper().strip()

        try:
            info = await asyncio.to_thread(lambda: yf.Ticker(symbol).info)

            # yfinance returns an empty or minimal dict for invalid tickers
            if not info or len(info) <= 1 or info.get("regularMarketPrice") is None:
                raise InvalidSymbolError(symbol, "stock")

            return info

        except InvalidSymbolError:
            raise
        except Exception as e:
            logger.error(f"Error fetching ticker {symbol}: {e}")
            raise APIError("Yahoo Finance", message=str(e))

    async def get_ticker_history(
        self, symbol: str, period: str = "5d"
    ) -> list[dict[str, Any]]:
        """
        Get historical price data for a ticker.

        Args:
            symbol: Stock ticker symbol.
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            List of dictionaries with OHLCV data.
        """
        logger.info(f"Fetching {period} history for: {symbol}")
        symbol = symbol.upper().strip()

        try:
            ticker = yf.Ticker(symbol)
            history = await asyncio.to_thread(lambda: ticker.history(period=period))

            if history.empty:
                return []

            records = []
            for index, row in history.iterrows():
                records.append({
                    "date": index.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                })
            return records

        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return []

    async def get_index_data(self, symbol: str) -> dict[str, Any]:
        """
        Get current data for a market index.

        Args:
            symbol: Index symbol (e.g., ^GSPC, ^IXIC, ^DJI)

        Returns:
            Dictionary with index data.
        """
        logger.info(f"Fetching index data for: {symbol}")

        try:
            info = await asyncio.to_thread(lambda: yf.Ticker(symbol).info)

            if not info or info.get("regularMarketPrice") is None:
                return {
                    "symbol": symbol,
                    "name": self.INDEX_NAMES.get(symbol, symbol),
                    "error": "Data not available",
                }

            return {
                "symbol": symbol,
                "name": self.INDEX_NAMES.get(symbol, info.get("shortName", symbol)),
                "price": info.get("regularMarketPrice"),
                "previous_close": info.get("regularMarketPreviousClose"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "day_high": info.get("regularMarketDayHigh"),
                "day_low": info.get("regularMarketDayLow"),
            }

        except Exception as e:
            logger.error(f"Error fetching index {symbol}: {e}")
            return {
                "symbol": symbol,
                "name": self.INDEX_NAMES.get(symbol, symbol),
                "error": str(e),
            }

    async def get_multiple_indices(
        self, symbols: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Get data for multiple indices concurrently.

        Args:
            symbols: List of index symbols. Defaults to major US indices.

        Returns:
            List of index data dictionaries.
        """
        if symbols is None:
            symbols = self.DEFAULT_INDICES

        tasks = [self.get_index_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "symbol": symbols[i],
                    "name": self.INDEX_NAMES.get(symbols[i], symbols[i]),
                    "error": str(result),
                })
            else:
                processed.append(result)

        return processed

    @staticmethod
    def is_market_open() -> dict[str, Any]:
        """
        Check if the US stock market is currently open.

        Returns:
            Dictionary with market status information.
        """
        now = datetime.now(timezone.utc)
        # NYSE opens at 14:30 UTC and closes at 21:00 UTC (9:30 AM - 4:00 PM ET)
        # This is approximate and doesn't account for holidays
        weekday = now.weekday()
        hour = now.hour
        minute = now.minute

        is_weekend = weekday >= 5
        is_trading_hours = (hour == 14 and minute >= 30) or (15 <= hour < 21)

        if is_weekend:
            status = "closed"
            reason = "Weekend"
        elif is_trading_hours:
            status = "open"
            reason = "Regular trading hours"
        elif hour < 14 or (hour == 14 and minute < 30):
            status = "pre_market"
            reason = "Pre-market hours"
        else:
            status = "after_hours"
            reason = "After-hours trading"

        return {
            "status": status,
            "reason": reason,
            "utc_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "note": "Does not account for US market holidays",
        }

    async def analyze_ticker(self, symbol: str) -> dict[str, Any]:
        """
        Get comprehensive analysis of a stock ticker.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            Dictionary with full stock analysis.
        """
        info = await self.get_ticker_info(symbol)
        history = await self.get_ticker_history(symbol, period="5d")

        # Calculate 5-day trend
        from .sentiment import analyze_price_trend

        closing_prices = [day["close"] for day in history] if history else []
        trend = analyze_price_trend(closing_prices)

        # Format market cap
        market_cap = info.get("marketCap")
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

        # Get description (first 200 chars)
        description = info.get("longBusinessSummary", "")
        if len(description) > 200:
            description = description[:197] + "..."

        return {
            "symbol": symbol.upper(),
            "name": info.get("shortName", info.get("longName", symbol)),
            "current_price": info.get("regularMarketPrice"),
            "previous_close": info.get("regularMarketPreviousClose"),
            "change": round(info.get("regularMarketChange", 0), 2),
            "change_percent": round(info.get("regularMarketChangePercent", 0), 2),
            "day_range": {
                "low": info.get("regularMarketDayLow"),
                "high": info.get("regularMarketDayHigh"),
            },
            "52_week_range": {
                "low": info.get("fiftyTwoWeekLow"),
                "high": info.get("fiftyTwoWeekHigh"),
            },
            "volume": info.get("regularMarketVolume"),
            "average_volume": info.get("averageVolume"),
            "market_cap": market_cap_str,
            "market_cap_raw": market_cap,
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": description,
            "5_day_trend": trend.value,
            "recent_prices": history[-5:] if history else [],
            "market_status": self.is_market_open(),
        }
