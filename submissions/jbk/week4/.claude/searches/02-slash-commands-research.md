# Custom Slash Commands (Skills) 조사

> 출처: https://code.claude.com/docs/en/skills

## 개요
- `.claude/commands/*.md` 또는 `.claude/skills/<name>/SKILL.md`로 생성
- 두 가지 모두 `/name`으로 호출 가능 (동일 기능)
- YAML frontmatter + Markdown 본문으로 구성

## 파일 위치별 적용 범위

| 위치 | 적용 범위 |
|------|----------|
| `~/.claude/skills/<name>/SKILL.md` | 모든 프로젝트 (개인) |
| `.claude/skills/<name>/SKILL.md` | 현재 프로젝트만 |
| `.claude/commands/<name>.md` | 현재 프로젝트만 (레거시, 동일 기능) |

## Frontmatter 필드

```yaml
---
name: my-skill              # 슬래시 커맨드 이름
description: 설명            # Claude가 언제 사용할지 판단하는 기준
argument-hint: [filename]   # 자동완성 시 힌트
disable-model-invocation: true  # Claude 자동 호출 방지 (수동만)
user-invocable: false       # /메뉴에서 숨기기
allowed-tools: Read, Grep   # 허용 도구 제한
model: sonnet               # 사용할 모델
context: fork               # 서브에이전트에서 실행
agent: Explore              # context: fork 시 사용할 에이전트
---
```

## 변수 치환

| 변수 | 설명 |
|------|------|
| `$ARGUMENTS` | 호출 시 전달된 모든 인자 |
| `$ARGUMENTS[N]` / `$N` | N번째 인자 (0-based) |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |

## 동적 컨텍스트 주입
- `` !`command` `` 문법으로 셸 명령어 결과를 스킬에 주입
- 예: `` !`gh pr diff` `` → PR diff 내용이 프롬프트에 삽입됨

## 예시: 테스트 러너

```yaml
---
name: run-tests
description: Run tests with coverage and report failures
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
---

Run the test suite for this project:

1. Run `make test` to execute all tests
2. If tests fail, analyze the failures and suggest fixes
3. If all pass, run coverage: `pytest --cov=backend/app backend/tests/`
4. Summarize results: passed/failed counts, coverage percentage
5. If coverage < 80%, suggest which files need more tests

Optional: test specific path with $ARGUMENTS
```

## 예시: 문서 동기화

```yaml
---
name: docs-sync
description: Sync API documentation with actual endpoints
disable-model-invocation: true
---

Sync API documentation:

1. Fetch the OpenAPI spec from /openapi.json
2. Read the current docs/API.md
3. Compare endpoints, methods, and schemas
4. Update docs/API.md with any changes
5. Report what changed (added/removed/modified endpoints)
```

## 핵심 팁
- 커맨드를 집중적이고 단일 목적으로 유지
- `$ARGUMENTS` 활용하여 유연성 확보
- 멱등(idempotent) 단계 선호
- `allowed-tools`로 안전한 도구만 허용
- `disable-model-invocation: true`로 위험한 작업은 수동 실행만 허용
