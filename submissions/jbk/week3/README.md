# Week 3 — MCP Movie Server (TMDB API)

TMDB(The Movie Database) API를 활용한 영화 정보 MCP 서버입니다.
**STDIO(로컬)**, **SSE**, **Streamable HTTP** transport를 지원하며, Streamable HTTP 모드에서는 OAuth 2.1 인증(API key 기반)을 적용합니다.

## Prerequisites

- Python 3.10+ (3.12 권장)
- conda + poetry
- TMDB API 키 ([themoviedb.org](https://www.themoviedb.org/settings/api)에서 발급)

## 환경 설정

```bash
# conda 환경 생성 및 활성화
conda create -n cs146s python=3.12 -y
conda activate cs146s

# 의존성 설치
poetry install --no-interaction
```

### 환경변수

`.env.example`을 `.env`로 복사하여 설정합니다:

| 변수 | 설명 | 필수 |
|------|------|------|
| `TMDB_ACCESS_TOKEN` | TMDB API v4 Bearer Token (JWT) | O |
| `TMDB_API_KEY` | TMDB API v3 Key (참고용) | X |
| `MCP_API_KEY` | OAuth 인가 시 사용자가 입력할 API key | Streamable HTTP 시 O |
| `MCP_SERVER_URL` | 외부 접속 URL (ngrok 등) | Streamable HTTP 시 O |

## 프로젝트 구조

```
server/
├── __init__.py    # 패키지 초기화
├── __main__.py    # python -m server 진입점
├── main.py        # 서버 팩토리 + CLI
├── auth.py        # OAuth 2.1 Provider (SimpleOAuthProvider)
├── tmdb.py        # TMDB API 클라이언트 + 포맷터
└── tools.py       # MCP tool 등록 (search, details, credits 등)
```

## 실행 방법

모든 커맨드는 `submissions/jbk/week3/` 디렉토리에서 실행합니다.

### 모드 1: STDIO (로컬, 기본값)

Claude Desktop이나 Claude Code에서 로컬로 사용합니다.

```bash
python -m server
# 또는 명시적으로:
python -m server --transport stdio
```

#### Claude Code 설정 (STDIO)

프로젝트 `.mcp.json`에 추가:

```json
{
  "mcpServers": {
    "movie-server": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "submissions/jbk/week3",
      "env": {
        "TMDB_ACCESS_TOKEN": "your_tmdb_access_token"
      }
    }
  }
}
```

### 모드 2: SSE (HTTP, 인증 없음)

HTTP SSE 서버로 실행합니다.

```bash
python -m server --transport sse --host 0.0.0.0 --port 8000
```

#### Claude Code 설정 (SSE)

프로젝트 `.mcp.json`에 추가:

```json
{
  "mcpServers": {
    "movie-server": {
      "type": "sse",
      "url": "https://your-ngrok-url.ngrok-free.app/sse"
    }
  }
}
```

### 모드 3: Streamable HTTP + OAuth 2.1 (권장)

OAuth 2.1 인증이 포함된 Streamable HTTP 서버로 실행합니다.
ngrok을 통해 외부에서 접근 가능합니다.

```bash
# 1. ngrok 터널 시작 (별도 터미널)
ngrok http 8000

# 2. 서버 시작
MCP_SERVER_URL="https://your-ngrok-url.ngrok-free.app" \
MCP_API_KEY="your-secret-key" \
python -m server --transport streamable-http --host 0.0.0.0 --port 8000
```

#### Claude Code 설정 (Streamable HTTP)

프로젝트 `.mcp.json`에 추가:

```json
{
  "mcpServers": {
    "movie-server": {
      "type": "http",
      "url": "https://your-ngrok-url.ngrok-free.app/mcp"
    }
  }
}
```

Claude Code 시작 시 브라우저가 열리고, `MCP_API_KEY`에 설정한 값을 입력하면 인증이 완료됩니다.

#### OAuth 인증 흐름

```
Claude Code → /register (동적 클라이언트 등록)
           → /authorize (브라우저 열림)
           → /auth/login (API key 입력 폼)
           → /auth/verify (검증 → 인가 코드 발급)
           → /token (access token 교환)
           → /mcp (MCP 통신 시작)
```

#### 자동 생성되는 엔드포인트

| Path | 역할 |
|------|------|
| `/.well-known/oauth-authorization-server` | OAuth AS 메타데이터 |
| `/.well-known/oauth-protected-resource` | Resource Server 메타데이터 |
| `/authorize` | 인가 엔드포인트 |
| `/token` | 토큰 교환 |
| `/register` | 동적 클라이언트 등록 |
| `/auth/login` | API key 입력 폼 |
| `/auth/verify` | API key 검증 |
| `/mcp` | MCP Streamable HTTP (Bearer auth) |

### CLI 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--transport` | `stdio` | `stdio`, `sse`, `streamable-http` |
| `--host` | `127.0.0.1` | 서버 바인드 호스트 |
| `--port` | `8000` | 서버 포트 |

## Tool Reference

### 1. `search_movie` — 영화 검색

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `query` | string | O | 검색할 영화 제목 또는 키워드 |
| `year` | int | X | 개봉 연도 필터 |

**예시:** `query="기생충"`, `year=2019`

### 2. `get_movie_details` — 영화 상세 정보

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `movie_id` | int | O | TMDB 영화 ID (search_movie로 확인) |

### 3. `get_recommendations` — 비슷한 영화 추천

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `movie_id` | int | O | 기준 영화의 TMDB ID |

### 4. `get_trending_movies` — 인기 영화 목록

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `time_window` | string | X | `"day"` (오늘, 기본값) 또는 `"week"` (이번 주) |

### 5. `get_movie_credits` — 출연진/제작진 조회

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `movie_id` | int | O | TMDB 영화 ID |

## 사용 흐름 예시

```
사용자: "기생충 영화 검색해줘"
→ search_movie(query="기생충")

사용자: "상세 정보 보여줘"
→ get_movie_details(movie_id=496243)

사용자: "출연진 알려줘"
→ get_movie_credits(movie_id=496243)

사용자: "비슷한 영화 추천해줘"
→ get_recommendations(movie_id=496243)

사용자: "요즘 인기 영화 뭐야?"
→ get_trending_movies(time_window="week")
```

## 기술 스택

- **MCP Framework:** FastMCP (mcp.server.fastmcp)
- **HTTP Client:** httpx (비동기)
- **Transport:** STDIO / SSE / Streamable HTTP
- **인증:** OAuth 2.1 (API key 기반, Streamable HTTP 모드)
- **외부 API:** TMDB API v3 (https://api.themoviedb.org/3)
- **기본 언어:** ko-KR (한국어)
