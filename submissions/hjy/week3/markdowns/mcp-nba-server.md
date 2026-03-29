# MCP NBA Server 구현 계획

## 목표
BALLDONTLIE API를 활용한 MCP 서버 구축 (Local STDIO + Remote HTTP)

## API 정보
- **Base URL**: `https://api.balldontlie.io/v1`
- **인증**: `Authorization: {API_KEY}` 헤더
- **Rate Limit**: 분당 5회
- **사용 가능 엔드포인트**: Teams, Players, Games

## MCP 도구 설계

### 1. `get_games`
- **설명**: 특정 날짜 또는 팀의 NBA 경기 조회
- **파라미터**:
  - `date` (optional): 경기 날짜 (YYYY-MM-DD)
  - `team` (optional): 팀 이름 또는 약칭 (예: "Lakers", "LAL")
- **반환**: 경기 목록 (홈팀, 원정팀, 점수, 상태)

### 2. `search_player`
- **설명**: NBA 선수 이름으로 검색
- **파라미터**:
  - `name` (required): 선수 이름 (예: "LeBron", "Curry")
- **반환**: 선수 정보 (이름, 팀, 포지션, 키, 몸무게)

### 3. `get_teams` (보너스)
- **설명**: NBA 팀 목록 조회
- **파라미터**:
  - `conference` (optional): "East" 또는 "West"
- **반환**: 팀 목록 (이름, 컨퍼런스, 디비전)

## 기술 스택
- **Python 3.12**
- **mcp** (MCP Python SDK)
- **httpx** (async HTTP client)
- **pydantic** (입력 검증)

## 폴더 구조
```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py          # MCP 서버 진입점
│   ├── api_client.py    # BALLDONTLIE API 클라이언트
│   ├── tools.py         # MCP 도구 정의
│   └── config.py        # 설정 (API key, rate limit)
├── tests/
│   ├── test_api_client.py
│   └── test_tools.py
├── README.md
├── pyproject.toml
└── .env.example
```

## 구현 단계

### Phase 1: Local (STDIO) - 기본 점수
1. [ ] 프로젝트 구조 및 의존성 설정
2. [ ] BALLDONTLIE API 클라이언트 구현
   - Rate limit 처리 (분당 5회)
   - 에러 핸들링 (타임아웃, HTTP 에러)
3. [ ] MCP 도구 구현 (get_games, search_player, get_teams)
4. [ ] STDIO 서버 구현 및 테스트
5. [ ] Claude Desktop 연동 테스트
6. [ ] README.md 작성

### Phase 2: Remote (HTTP) - 보너스 +5점
7. [ ] HTTP transport 추가
8. [ ] Vercel 또는 Cloudflare 배포
9. [ ] 배포 문서 추가

### Phase 3: Authentication - 보너스 +5점
10. [ ] API key 기반 인증 구현
11. [ ] 인증 문서 추가

## 에러 처리 전략
- **Rate Limit (429)**: 재시도 전 60초 대기 안내
- **Timeout**: 10초 타임아웃, graceful 에러 메시지
- **404/Empty**: "결과를 찾을 수 없습니다" 반환
- **5xx**: "API 서버 오류, 잠시 후 재시도" 반환

## 테스트 케이스
1. API 클라이언트
   - 정상 응답 파싱
   - Rate limit 에러 처리
   - 타임아웃 처리
2. MCP 도구
   - 유효한 입력으로 정상 동작
   - 잘못된 입력 검증
   - 빈 결과 처리

## Claude Desktop 설정 예시
```json
{
  "mcpServers": {
    "nba": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/week3",
      "env": {
        "BALLDONTLIE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## 리스크
- Rate limit이 분당 5회로 매우 제한적 → 캐싱 또는 사용자 안내 필요
- Free plan에서 박스스코어 미지원 → Games 기본 정보만 제공
