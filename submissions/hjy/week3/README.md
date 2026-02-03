# MCP NBA Server

BALLDONTLIE API를 활용한 NBA 데이터 MCP 서버입니다. Claude Desktop 또는 MCP 클라이언트에서 NBA 팀, 선수, 경기 정보를 조회할 수 있습니다.

## Deployment Options

| Mode | Transport | URL |
|------|-----------|-----|
| **Local** | STDIO | Claude Desktop에서 로컬 실행 |
| **Remote** | HTTP (Streamable) | https://vercel-server-umber.vercel.app/api/mcp |

### Authentication (Remote)

Remote 서버는 Bearer Token 인증이 필요합니다:
- **API Key**: `nba-mcp-secret-key-2025`
- **Header**: `Authorization: Bearer nba-mcp-secret-key-2025`

## Prerequisites

- Python 3.10+
- [BALLDONTLIE API Key](https://www.balldontlie.io/) (무료 가입)

## Setup

### 1. 의존성 설치

```bash
cd week3
pip install -e ".[dev]"
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열고 API 키 입력
```

```env
BALLDONTLIE_API_KEY=your-api-key-here
```

### 3. 테스트 실행

```bash
python -m pytest tests/ -v
```

## Claude Desktop 연동

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일에 다음을 추가하세요:

```json
{
  "mcpServers": {
    "nba": {
      "command": "/opt/miniconda3/envs/cs146s/bin/python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/week3",
      "env": {
        "BALLDONTLIE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

> **Note**: `command`와 `cwd` 경로를 실제 환경에 맞게 수정하세요.

Claude Desktop을 재시작하면 MCP 도구가 활성화됩니다.

## MCP Tools

### 1. `get_teams`

NBA 팀 목록을 조회합니다.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `conference` | string | No | `"East"` 또는 `"West"`로 필터링 |

**Example:**
```
"서부 컨퍼런스 팀들 알려줘"
"NBA 팀 목록 보여줘"
```

**Output:**
```
NBA Teams (30 total):

=== Eastern Conference ===
  Atlanta Hawks (ATL) - East Conference, Southeast Division
  Boston Celtics (BOS) - East Conference, Atlantic Division
  ...

=== Western Conference ===
  Dallas Mavericks (DAL) - West Conference, Southwest Division
  ...
```

### 2. `search_player`

NBA 선수를 이름으로 검색합니다.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | Yes | 선수 이름 (최소 2글자) |

**Example:**
```
"LeBron James 정보 알려줘"
"Curry 선수 검색해줘"
```

**Output:**
```
Players matching 'LeBron' (1 found):

  • LeBron James - Los Angeles Lakers, #23, Position: F, Height: 6-9, Weight: 250 lbs
```

### 3. `get_games`

NBA 경기를 조회합니다.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `date` | string | No | 경기 날짜 (`YYYY-MM-DD` 형식) |
| `team` | string | No | 팀 이름, 도시명, 또는 약칭 |

**Example:**
```
"오늘 Lakers 경기 있어?"
"2025-01-15 경기 결과 알려줘"
"Warriors 최근 경기"
```

**Output:**
```
NBA Games on 2025-01-15 for Lakers (1 games):

  • [2025-01-15] Final: Boston Celtics 105 @ Los Angeles Lakers 110
```

## Rate Limiting

BALLDONTLIE Free Plan은 **분당 5회** 요청 제한이 있습니다. 제한 초과 시 다음 메시지가 표시됩니다:

```
Rate limit exceeded. Please wait 60 seconds before trying again.
```

## Project Structure

```
week3/
├── server/                    # Local STDIO 서버 (Python)
│   ├── __init__.py
│   ├── main.py               # MCP 서버 진입점
│   ├── api_client.py         # BALLDONTLIE API 클라이언트
│   ├── tools.py              # MCP 도구 정의
│   └── config.py             # 설정
├── vercel-server/             # Remote HTTP 서버 (TypeScript)
│   ├── app/
│   │   ├── api/mcp/route.ts  # MCP 엔드포인트 + Bearer Auth
│   │   └── .well-known/      # OAuth 메타데이터
│   ├── package.json
│   └── tsconfig.json
├── tests/
│   ├── test_api_client.py
│   └── test_tools.py
├── markdowns/
│   └── mcp-nba-server.md     # 구현 계획
├── README.md
├── pyproject.toml
└── .env.example
```

## Error Handling

| Error | Response |
|-------|----------|
| Rate Limit (429) | "Rate limit exceeded. Please wait X seconds." |
| Timeout | "Request timed out after 10 seconds." |
| Network Error | "Network error: {details}" |
| Unknown Team | "Unknown team '{name}'. Try using the full team name..." |
| No Results | "No games/players/teams found for {criteria}." |

## Remote Server (Vercel)

### MCP Client 설정 (Cursor 등)

`.cursor/mcp.json` 또는 MCP 클라이언트 설정:

```json
{
  "mcpServers": {
    "nba-remote": {
      "url": "https://vercel-server-umber.vercel.app/api/mcp",
      "headers": {
        "Authorization": "Bearer nba-mcp-secret-key-2025"
      }
    }
  }
}
```

### Remote Server 구조

```
vercel-server/
├── app/
│   ├── api/mcp/route.ts       # MCP 엔드포인트 + 인증
│   ├── .well-known/           # OAuth 메타데이터
│   ├── layout.tsx
│   └── page.tsx
├── package.json
└── tsconfig.json
```

## Development

```bash
# Local (Python) 테스트
python -m pytest tests/ -v

# Remote (TypeScript) 개발
cd vercel-server
npm run dev

# 린트
ruff check server/

# 포맷팅
black server/ tests/
```
