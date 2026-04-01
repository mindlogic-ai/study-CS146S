# Investment Helper MCP Server

A Model Context Protocol (MCP) server for investment decision-making that aggregates stock prices, cryptocurrency data, and market trends using free APIs that require no authentication.

**Live deployment**: https://investment-helper-mcp-production.up.railway.app

## Overview

This MCP server provides three tools to help with investment research:

1. **Market Briefing** - Morning overview of major stock indices and crypto markets
2. **Stock Analysis** - Detailed analysis of individual stock tickers
3. **Crypto Analysis** - Comprehensive cryptocurrency analysis with insights

## APIs Used

### 1. Yahoo Finance (via yfinance library)

- **Type**: Python library wrapping Yahoo Finance endpoints
- **Authentication**: None required
- **Endpoints used**:
  - Stock quotes: current price, daily change, volume
  - Historical data: 52-week high/low, price history
  - Stock info: market cap, sector, P/E ratio, company description
- **Rate limits**: Unofficial API, ~2000 requests/hour is safe
- **Documentation**: https://pypi.org/project/yfinance/

### 2. CoinGecko API (free tier)

- **Base URL**: `https://api.coingecko.com/api/v3`
- **Authentication**: None required for free tier
- **Endpoints used**:
  - `GET /global` - Total crypto market cap, dominance percentages
  - `GET /coins/markets` - Top coins by market cap with prices
  - `GET /coins/{id}` - Detailed coin data with community sentiment
  - `GET /search/trending` - Trending coins in last 24 hours
- **Rate limits**: 10-30 calls/minute on free tier
- **Documentation**: https://docs.coingecko.com/reference/introduction

## Prerequisites

- Python 3.11 or higher
- No API keys required

## Setup Instructions

1. **Navigate to the week3 directory**:
   ```bash
   cd week3
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file (optional)**:
   ```bash
   cp .env.example .env
   ```

## How to Run

### Option 1: Local STDIO Mode (for Claude Desktop)

Start the server in STDIO mode:

```bash
python -m server.main
```

The server will start and wait for MCP protocol messages on stdin/stdout.

### Option 2: Local HTTP/SSE Mode (for testing remote transport)

Start the server in HTTP mode:

```bash
# Set API key for authentication
export API_KEY="your-secret-key"

# Start HTTP server
python -m server.http
```

The server will start on `http://localhost:8000` with:
- `GET /health` - Health check (no auth required)
- `GET /sse` - SSE endpoint for MCP connections (auth required)
- `POST /messages` - Message handling endpoint (auth required)

Test with:
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"investment-helper-mcp","transport":"sse"}
```

## Claude Desktop Configuration

To use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "investment-helper": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/absolute/path/to/week3"
    }
  }
}
```

Replace `/absolute/path/to/week3` with the actual path to the week3 directory.

### Alternative: Using venv Python directly

```json
{
  "mcpServers": {
    "investment-helper": {
      "command": "/absolute/path/to/week3/venv/bin/python",
      "args": ["-m", "server.main"],
      "cwd": "/absolute/path/to/week3"
    }
  }
}
```

## Remote Deployment (Railway)

```bash
# Install CLI and login
brew install railway
railway login

# Deploy
railway init                    # Select "Empty Project"
railway variables set API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
railway up
railway domain                  # Get your URL
```

**Authentication**: All endpoints except `/health` require `Authorization: Bearer <API_KEY>` header.

```bash
# Test
curl https://investment-helper-mcp-production.up.railway.app/health
curl -H "Authorization: Bearer YOUR_API_KEY" https://investment-helper-mcp-production.up.railway.app/sse
```

## Tool Reference

### 1. `get_market_briefing`

Get a morning briefing of stock indices and crypto market overview.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_crypto` | boolean | `true` | Include cryptocurrency summary |
| `indices` | array | `["^GSPC", "^IXIC", "^DJI"]` | Index symbols to include |

**Common Index Symbols**:
- `^GSPC` - S&P 500
- `^IXIC` - NASDAQ Composite
- `^DJI` - Dow Jones Industrial Average
- `^RUT` - Russell 2000
- `^VIX` - VIX Volatility Index

**Example Input**:
```json
{}
```

**Example Output**:
```json
{
  "briefing_type": "market_overview",
  "market_status": {
    "status": "open",
    "reason": "Regular trading hours"
  },
  "indices": [
    {
      "symbol": "^GSPC",
      "name": "S&P 500",
      "price": 5234.18,
      "change": 15.23,
      "change_percent": 0.29,
      "direction": "up"
    }
  ],
  "major_crypto": {
    "bitcoin": { "price": "$67,234.00", "change_24h": 2.15 },
    "ethereum": { "price": "$3,456.00", "change_24h": 1.82 }
  },
  "trending_crypto": [
    { "name": "Solana", "symbol": "SOL", "rank": 5 }
  ],
  "summary": "S&P 500: 5,234.18 (▲ 0.29%) | BTC: $67,234.00 (▲ 2.15%)"
}
```

### 2. `analyze_ticker`

Get detailed analysis of a stock ticker.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | Yes | Stock ticker symbol (e.g., NVDA, AAPL, TSLA) |

**Example Input**:
```json
{"symbol": "NVDA"}
```

**Example Output**:
```json
{
  "symbol": "NVDA",
  "name": "NVIDIA Corporation",
  "current_price": "$875.28",
  "change": {
    "amount": 12.45,
    "percent": 1.44,
    "direction": "up"
  },
  "52_week_range": {
    "low": 373.56,
    "high": 974.00
  },
  "market_cap": "$2.16T",
  "valuation": {
    "pe_ratio": 65.23,
    "forward_pe": 42.15
  },
  "sector": "Technology",
  "industry": "Semiconductors",
  "trend_analysis": {
    "5_day_trend": "bullish",
    "trend_description": "Positive trend over the past 5 days"
  },
  "highlights": [
    "Trading near 52-week high",
    "Strong upward price momentum recently"
  ]
}
```

### 3. `get_crypto_analysis`

Get detailed analysis of a cryptocurrency.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `coin_id` | string | Yes | CoinGecko coin ID (lowercase) |

**Common Coin IDs**: `bitcoin`, `ethereum`, `solana`, `cardano`, `dogecoin`, `ripple`, `polkadot`

**Example Input**:
```json
{"coin_id": "bitcoin"}
```

**Example Output**:
```json
{
  "coin_id": "bitcoin",
  "symbol": "BTC",
  "name": "Bitcoin",
  "current_price": "$67,234.00",
  "market_cap": "$1.32T",
  "market_cap_rank": 1,
  "price_changes": {
    "24h": { "value": "+2.15%", "direction": "up" },
    "7d": { "value": "+5.82%", "direction": "up" },
    "30d": { "value": "-3.21%", "direction": "down" }
  },
  "all_time_high": {
    "price": "$69,000.00",
    "date": "2021-11-10",
    "change_from_ath": "-2.6%"
  },
  "supply": {
    "circulating": "19.6M",
    "max": "21M",
    "percent_circulating": "93.5%"
  },
  "community_sentiment": {
    "up_votes": 78,
    "down_votes": 22
  },
  "analysis": {
    "overall_sentiment": "bullish",
    "bullish_signals": ["Strong community sentiment", "Near all-time high"],
    "insights": ["Top 10 cryptocurrency by market cap (#1)"]
  }
}
```

## Example Conversation Flow

**User**: "What's the market looking like today?"

**Claude**: *[calls get_market_briefing]*
> The markets are mixed today. The S&P 500 is up 0.29% at 5,234, while NASDAQ gained 0.45%. Bitcoin is trading at $67,234 (+2.15%) and Ethereum at $3,456 (+1.82%). Trending coins include Solana and Cardano.

**User**: "Tell me about NVIDIA stock"

**Claude**: *[calls analyze_ticker with symbol="NVDA"]*
> NVIDIA (NVDA) is currently trading at $875.28, up 1.44% today. Key highlights:
> - 52-week range: $373.56 - $974.00 (trading near the high)
> - Market cap: $2.16 trillion
> - P/E ratio: 65.23 (forward P/E: 42.15)
> - 5-day trend: Bullish with positive momentum

**User**: "How's Ethereum doing?"

**Claude**: *[calls get_crypto_analysis with coin_id="ethereum"]*
> Ethereum (ETH) is trading at $3,456.00:
> - 24h: +1.82% | 7d: +4.21% | 30d: -2.15%
> - Market cap: $415B (rank #2)
> - All-time high: $4,891 (Nov 2021), currently 29% below ATH
> - 93% of max supply in circulation
> - Community sentiment: 72% positive

## Error Handling

The server handles errors gracefully:

- **Invalid symbols**: Returns helpful error with suggestions
- **Rate limits**: Warns when CoinGecko rate limit is approached
- **Network timeouts**: 10-second timeout with clear error messages
- **API failures**: Structured error responses with recovery suggestions

Example error response:
```json
{
  "error": true,
  "message": "Stock symbol 'INVALID' not found",
  "suggestion": "Check the symbol spelling. Common symbols: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA"
}
```

## Project Structure

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP server entrypoint (STDIO transport)
│   ├── http.py              # MCP server entrypoint (HTTP/SSE transport)
│   ├── config.py            # Settings management
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── market_briefing.py
│   │   ├── ticker_analysis.py
│   │   └── crypto_analysis.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── yahoo_finance.py  # yfinance wrapper
│   │   ├── coingecko.py      # CoinGecko API wrapper
│   │   └── sentiment.py      # Trend-based sentiment analysis
│   └── utils/
│       ├── __init__.py
│       ├── rate_limiter.py   # Simple rate limiting
│       └── errors.py         # Custom exceptions
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── Procfile                 # Railway start command
└── railway.json             # Railway deployment config
```

## Development Notes

- **STDIO mode**: All logging goes to stderr (stdout is reserved for MCP protocol)
- **HTTP mode**: Logging goes to stdout (visible in Railway logs)
- yfinance calls are wrapped in `asyncio.to_thread()` for async compatibility
- CoinGecko rate limiter tracks calls in a sliding 60-second window
- Market hours detection is approximate and doesn't account for US holidays
- HTTP transport uses SSE (Server-Sent Events) for server-to-client streaming

## License

MIT
