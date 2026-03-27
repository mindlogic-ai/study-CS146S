# FactChat Multi-LLM Compare MCP Server

FactChat API를 활용하여 동일한 프롬프트를 여러 LLM 모델에 동시에 보내고 응답을 비교하는 MCP (Model Context Protocol) 서버입니다.

## Prerequisites

- Python 3.10 이상 (3.12 권장)
- uv (Python 패키지 관리자)
- FactChat API 키 (mindlogic.ai에서 발급)

## Setup

### 1. uv 설치 (아직 없다면)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 프로젝트 디렉토리로 이동

```bash
cd submissions/mjk/week3
```

### 3. 의존성 설치

```bash
uv sync
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어서 FACTCHAT_API_KEY에 실제 API 키를 입력하세요
```

### 5. 서버 실행 테스트 (선택)

```bash
uv run python -m server.main
```

STDIO 모드이므로 직접 실행하면 MCP 프로토콜 메시지가 표시됩니다. Claude Desktop에서 사용하는 것이 일반적입니다.

## Claude Desktop 연동

### macOS 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일을 편집:

```json
{
  "mcpServers": {
    "factchat-compare": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/minjae/mindlogic/study-CS146S/submissions/mjk/week3",
        "run",
        "python",
        "-m",
        "server.main"
      ],
      "env": {
        "FACTCHAT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**주의**:
- `/Users/minjae/...` 경로를 실제 프로젝트 절대 경로로 변경하세요
- `FACTCHAT_API_KEY`에 실제 API 키를 입력하세요
- 설정 후 Claude Desktop을 완전히 종료했다가 다시 시작하세요

### Windows 설정

`%APPDATA%\Claude\claude_desktop_config.json` 파일을 편집 (경로를 Windows 형식으로 변경):

```json
{
  "mcpServers": {
    "factchat-compare": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\submissions\\mjk\\week3",
        "run",
        "python",
        "-m",
        "server.main"
      ],
      "env": {
        "FACTCHAT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Tool Reference

### list_models

사용 가능한 모든 LLM 모델 목록을 조회합니다.

**파라미터**: 없음

**반환**: JSON 형식의 모델 목록

```json
{
  "total": 6,
  "models": [
    {
      "model_id": "claude-sonnet-4-5-20250929",
      "provider": "anthropic",
      "display_name": "Claude Sonnet 4.5",
      "description": "Anthropic의 균형 잡힌 성능의 중급 모델"
    },
    ...
  ]
}
```

**예시 호출**:
- "어떤 모델들을 사용할 수 있나요?"
- "사용 가능한 모델 목록을 보여줘"

### compare_models

선택한 모델들에 동일한 프롬프트를 동시에 보내고 응답을 비교합니다.

**파라미터**:
- `prompt` (필수, string): 모델에 보낼 프롬프트
- `model_ids` (선택, array): 비교할 모델 ID 배열. 미지정 시 전체 6개 모델 대상
- `max_tokens` (선택, integer): 최대 응답 토큰 수. 기본값 1024

**반환**: JSON 형식의 비교 결과 (latency 순 정렬)

```json
{
  "prompt": "양자 컴퓨팅을 초등학생에게 설명해주세요",
  "models_queried": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "model_id": "claude-haiku-4-5-20251001",
      "display_name": "Claude Haiku 4.5",
      "provider": "anthropic",
      "latency_ms": 1234.5,
      "status": "success",
      "content": "양자 컴퓨팅이란...",
      "input_tokens": 15,
      "output_tokens": 200
    },
    ...
  ]
}
```

**예시 호출**:
- "Claude Sonnet과 GPT-5로 '양자 컴퓨팅이란?' 물어보고 비교해줘"
- "전체 모델에 같은 질문 보내기: 인공지능의 미래는?"
- "gpt-5와 gpt-5-mini로 간단한 코드 작성 비교"

## Example Invocation Flow

1. **Claude Desktop 시작** — 서버가 자동 연결되면 🔌 아이콘이 나타남
2. **모델 목록 조회**:
   ```
   사용자: "사용 가능한 모델 목록을 보여줘"
   Claude: [list_models 도구 호출] → 6개 모델 정보 표시
   ```
3. **모델 비교**:
   ```
   사용자: "claude-sonnet-4-5-20250929와 gpt-5에게 같은 질문을 보내서 비교해줘:
           한국어로 인공지능의 미래에 대해 설명해주세요"
   Claude: [compare_models 도구 호출] → 두 모델의 응답, 지연시간, 토큰 사용량 비교
   ```
4. **전체 모델 비교**:
   ```
   사용자: "모든 모델에게 '파이썬과 자바스크립트의 차이점 3가지'를 물어보고 비교해줘"
   Claude: [compare_models 도구 호출 (model_ids 미지정)] → 6개 모델 전부 비교
   ```

## Supported Models

| Model ID | Provider | Display Name | Description |
|----------|----------|-------------|-------------|
| `claude-sonnet-4-5-20250929` | Anthropic | Claude Sonnet 4.5 | 균형 잡힌 성능의 중급 모델 |
| `claude-opus-4-5-20251101` | Anthropic | Claude Opus 4.5 | 최고 성능 플래그십 모델 |
| `claude-haiku-4-5-20251001` | Anthropic | Claude Haiku 4.5 | 빠르고 경제적인 경량 모델 |
| `gpt-5.1-chat-latest` | OpenAI | GPT-5.1 | 최신 고성능 모델 |
| `gpt-5` | OpenAI | GPT-5 | 범용 플래그십 모델 |
| `gpt-5-mini` | OpenAI | GPT-5 Mini | 경량 고속 모델 |

## Error Handling

서버는 다음과 같은 에러를 graceful하게 처리합니다:

| 에러 유형 | 응답 |
|----------|------|
| API 키 미설정 | "FACTCHAT_API_KEY 환경 변수가 설정되지 않았습니다" |
| 유효하지 않은 모델 ID | 에러 메시지 + 사용 가능한 모델 목록 |
| HTTP 타임아웃 (60초 초과) | 해당 모델만 error 표시, 나머지 정상 반환 |
| HTTP 401 (인증 실패) | "인증 실패 - API 키를 확인하세요" |
| HTTP 429 (Rate Limit) | "Rate limit 초과 - 잠시 후 다시 시도하세요" |
| HTTP 5xx (서버 오류) | "서버 오류 (HTTP {status})" |

**핵심 특징**: 한 모델의 실패가 다른 모델의 결과에 영향을 주지 않습니다. 각 모델 호출은 독립적으로 에러를 처리합니다.

## Development

### 코드 포맷팅

```bash
uv run black server/
```

### 린팅

```bash
uv run ruff check server/
```

### 테스트 (선택)

```bash
uv run pytest
```

## Architecture

```
FastMCP (STDIO) → Tool (list_models, compare_models)
                       ↓
                  client.py (httpx + asyncio.gather)
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
    Anthropic API        OpenAI API
    (factchat-cloud)    (factchat-cloud)
```

**핵심 기술**:
- **FastMCP**: 데코레이터 기반 MCP 도구 등록
- **asyncio.gather**: 모든 모델에 동시 요청 (총 소요시간 = 가장 느린 모델 하나)
- **httpx.AsyncClient**: 비동기 HTTP 클라이언트 (connection pooling)
- **개별 에러 격리**: 예외를 전파하지 않고 ModelResponse.error에 기록

## Troubleshooting

### "Import server.config could not be resolved"
- 이는 IDE 경고입니다. 실행 시 `python -m server.main` 형식으로 실행하면 정상 동작합니다.

### Claude Desktop에서 서버가 연결되지 않음
1. `claude_desktop_config.json` 파일 경로 확인
2. JSON 문법 오류 확인 (쉼표, 따옴표 등)
3. 절대 경로가 올바른지 확인
4. Claude Desktop 완전 종료 후 재시작
5. Claude Desktop 로그 확인: `~/Library/Logs/Claude/mcp*.log` (macOS)

### API 키 오류
- `.env` 파일에 올바른 키가 있는지 확인
- Claude Desktop 설정의 `env.FACTCHAT_API_KEY`에도 키가 있는지 확인
- 둘 중 하나만 있으면 되며, Claude Desktop 설정의 값이 우선합니다

## License

MIT
