"""Simple trend-based sentiment analysis."""

from enum import Enum


class TrendSentiment(str, Enum):
    """Sentiment classification based on price trends."""

    STRONGLY_BULLISH = "strongly_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONGLY_BEARISH = "strongly_bearish"
    INSUFFICIENT_DATA = "insufficient_data"


def analyze_price_trend(prices: list[float]) -> TrendSentiment:
    """
    Analyze recent price trend from a list of closing prices.

    Args:
        prices: List of closing prices in chronological order.

    Returns:
        TrendSentiment indicating the direction and strength of the trend.
    """
    if len(prices) < 2:
        return TrendSentiment.INSUFFICIENT_DATA

    start, end = prices[0], prices[-1]

    if start == 0:
        return TrendSentiment.INSUFFICIENT_DATA

    change_pct = ((end - start) / start) * 100

    if change_pct > 5:
        return TrendSentiment.STRONGLY_BULLISH
    elif change_pct > 1:
        return TrendSentiment.BULLISH
    elif change_pct < -5:
        return TrendSentiment.STRONGLY_BEARISH
    elif change_pct < -1:
        return TrendSentiment.BEARISH
    return TrendSentiment.NEUTRAL


def get_sentiment_emoji(sentiment: TrendSentiment) -> str:
    """Get an emoji representation of the sentiment."""
    emoji_map = {
        TrendSentiment.STRONGLY_BULLISH: "📈🚀",
        TrendSentiment.BULLISH: "📈",
        TrendSentiment.NEUTRAL: "➡️",
        TrendSentiment.BEARISH: "📉",
        TrendSentiment.STRONGLY_BEARISH: "📉🔻",
        TrendSentiment.INSUFFICIENT_DATA: "❓",
    }
    return emoji_map.get(sentiment, "")
