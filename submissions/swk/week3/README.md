# Week 3 — CoinGecko MCP Server

CoinGecko API를 감싸는 MCP(Model Context Protocol) 서버입니다. 암호화폐 시세, 상세 정보, 트렌딩 코인을 조회할 수 있습니다.

**두 가지 배포 모드를 지원합니다:**
- **Local (STDIO):** `server/` — Claude Desktop, Cursor 등에서 로컬 실행
- **Remote (HTTP):** `server-remote/` — Vercel에 배포, Streamable HTTP로 접근
  - Production URL: `https://coingecko-mcp-swk.vercel.app/api/mcp`

## Prerequisites

- Node.js 16+
- (선택) CoinGecko Demo API Key — [무료 발급](https://www.coingecko.com/en/api/pricing)

## Setup

```bash
cd week3/server
npm install
npm run build
```

### 환경 변수

```bash
cp .env.example .env
# .env 파일에 COINGECKO_API_KEY 설정 (선택)
```

API 키 없이도 동작하지만 rate limit이 낮습니다 (5-15 calls/min). 키를 등록하면 30 calls/min으로 올라갑니다.

## Run

```bash
# STDIO 모드로 직접 실행
node build/index.js

# 또는 API 키와 함께
COINGECKO_API_KEY=your_key node build/index.js
```

## Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coingecko": {
      "command": "node",
      "args": ["/ABSOLUTE/PATH/TO/week3/server/build/index.js"],
      "env": {
        "COINGECKO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

설정 후 Claude Desktop을 재시작하세요.

## Remote (HTTP) — Vercel 배포

원격 MCP 서버가 Vercel에 배포되어 있습니다.

**Endpoint:** `https://coingecko-mcp-swk.vercel.app/api/mcp`

### 인증 (API 키)

서버에 `MCP_API_KEY` 환경변수가 설정되어 있으면 Bearer 토큰 인증이 필수입니다.
유효하지 않은 토큰으로 요청하면 401 Unauthorized가 반환됩니다.

- 클라이언트의 Bearer 토큰은 MCP 서버 접근 제어에만 사용됩니다.
- CoinGecko API 키는 서버 내부에서만 사용되며, 클라이언트 토큰이 업스트림에 전달되지 않습니다.
- `MCP_API_KEY`가 설정되지 않으면 인증 없이 접근 가능합니다 (개발/테스트용).

### Claude Desktop에서 사용 (mcp-remote)

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coingecko-remote": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://coingecko-mcp-swk.vercel.app/api/mcp",
        "--header",
        "Authorization: Bearer YOUR_MCP_API_KEY"
      ]
    }
  }
}
```

### 직접 배포

```bash
cd week3/server-remote
npm install
vercel login
vercel env add COINGECKO_API_KEY   # CoinGecko API 키
vercel env add MCP_API_KEY         # MCP 서버 접근용 API 키
vercel --prod
```

## 예제 호출 흐름 (Claude Desktop)

1. Claude Desktop을 실행하고 새 대화를 시작합니다.
2. 채팅창 하단의 **"+"** 아이콘을 클릭합니다.
3. **Connectors** 메뉴에서 **coingecko** 서버가 표시되는지 확인합니다. (3개 tool이 보여야 정상)
4. 채팅창에 자연어로 질문을 입력합니다:

```
비트코인이랑 이더리움 현재 가격 알려줘
```

5. Claude가 `get_coin_markets` tool 호출을 제안합니다. **"Allow"** 버튼을 클릭하여 승인합니다.
6. tool이 실행되고, CoinGecko API에서 가져온 실시간 시세가 응답에 포함됩니다.

### 추가 질문 예시

| 질문 | 호출되는 Tool |
|------|--------------|
| "상위 20개 코인 시세 보여줘" | `get_coin_markets` |
| "솔라나 상세 정보 알려줘" | `get_coin_detail` |
| "요즘 뜨는 코인 뭐야?" | `get_trending` |
| "비트코인 원화 가격은?" | `get_coin_markets` (vs_currency=krw) |

## Tool Reference

### 1. `get_coin_markets`

시가총액 기준 상위 코인 또는 특정 코인의 시세를 조회합니다.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vs_currency` | string | `"usd"` | 표시 통화 (usd, eur, krw 등) |
| `ids` | string? | — | 쉼표 구분 코인 ID (예: `bitcoin,ethereum`) |
| `per_page` | number | `10` | 결과 개수 (1-50) |

**예시 입력:** "비트코인과 이더리움 현재 가격 알려줘"

**예시 출력:**
```
1. Bitcoin (BTC)
   Price: $104,250
   24h: +2.35%  |  Vol: $28,500,000,000
   High/Low: $105,000 / $101,800

2. Ethereum (ETH)
   Price: $3,280
   24h: +1.12%  |  Vol: $12,300,000,000
   High/Low: $3,310 / $3,200
```

### 2. `get_coin_detail`

특정 코인의 상세 정보를 조회합니다 (설명, 가격 변동, 공급량).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `coin_id` | string | — | CoinGecko 코인 ID (예: `bitcoin`) |
| `vs_currency` | string | `"usd"` | 표시 통화 |

**예시 입력:** "솔라나 상세 정보 보여줘"

**예시 출력:**
```
# Solana (SOL)

Solana is a high-performance blockchain...

## Market Data (USD)
Price: $178.50
Market Cap: $82,000,000,000
24h Volume: $3,200,000,000

## Price Changes
24h: +3.45%
7d:  +12.30%
30d: -5.20%

## Supply
Circulating: 460,000,000
Total: 580,000,000
Max: N/A
```

### 3. `get_trending`

CoinGecko에서 검색량 기준 트렌딩 코인을 조회합니다.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| (없음) | — | — | 파라미터 없음 |

**예시 입력:** "요즘 뜨는 코인 뭐야?"

**예시 출력:**
```
# Trending Coins

1. Pepe (PEPE) — Rank #25 | 24h: +15.30%
2. Bonk (BONK) — Rank #60 | 24h: +8.20%
3. Worldcoin (WLD) — Rank #80 | 24h: +5.10%
...
```

## 사용한 CoinGecko API 엔드포인트

| Endpoint | 용도 |
|----------|------|
| `GET /coins/markets` | 코인 시세 목록 |
| `GET /coins/{id}` | 코인 상세 정보 |
| `GET /search/trending` | 트렌딩 코인 |

## 에러 처리

- **Rate Limit (429):** 최대 3회 재시도, 2초씩 증가하는 백오프 (2s → 4s → 6s). 재시도 실패 시 사용자에게 대기 안내 메시지 반환
- **타임아웃:** 요청당 15초 제한. 타임아웃 시 자동 재시도 (최대 3회)
- **HTTP 오류:** 상태 코드와 함께 에러 메시지 전달
- **빈 결과:** 데이터 없음 안내 메시지 반환
- 모든 에러는 `isError: true` 플래그와 함께 MCP 클라이언트에 전달
- 재시도 로그는 `stderr`로 출력 (STDIO 프로토콜과 충돌 없음)

## 프로젝트 구조

```
week3/
├── README.md
├── assignment.md
├── server/                    # Local STDIO 서버
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   ├── src/
│   │   └── index.ts
│   └── build/
│       └── index.js
└── server-remote/             # Remote HTTP 서버 (Vercel)
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts
    └── app/
        └── api/
            └── mcp/
                └── route.ts   # MCP 핸들러
```
