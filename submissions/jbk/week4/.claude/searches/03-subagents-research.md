# SubAgents 조사

> 출처: https://code.claude.com/docs/en/sub-agents

## 개요
- 특화된 AI 에이전트로, 각각 독립된 컨텍스트 윈도우에서 실행
- 고유한 시스템 프롬프트, 도구 접근, 독립 권한 보유
- Claude가 매칭되는 작업을 만나면 자동 위임

## 장점
- **컨텍스트 보존**: 탐색/구현을 메인 대화에서 분리
- **제약 적용**: 서브에이전트 사용 가능 도구 제한
- **행동 특화**: 도메인별 시스템 프롬프트
- **비용 제어**: Haiku 등 저비용 모델 라우팅 가능

## 빌트인 서브에이전트

| 이름 | 모델 | 도구 | 용도 |
|------|------|------|------|
| Explore | Haiku | 읽기 전용 | 코드베이스 탐색/검색 |
| Plan | 상속 | 읽기 전용 | 계획 모드 리서치 |
| general-purpose | 상속 | 전체 | 복잡한 다단계 작업 |

## 커스텀 서브에이전트 생성

### 파일 위치

| 위치 | 범위 | 우선순위 |
|------|------|---------|
| `--agents` CLI 플래그 | 현재 세션만 | 1 (최고) |
| `.claude/agents/` | 현재 프로젝트 | 2 |
| `~/.claude/agents/` | 모든 프로젝트 | 3 |

### 파일 형식
YAML frontmatter + Markdown 시스템 프롬프트:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

### Frontmatter 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | Yes | 고유 식별자 (소문자 + 하이픈) |
| `description` | Yes | 언제 위임할지 설명 |
| `tools` | No | 사용 가능 도구 (미지정 시 전체 상속) |
| `disallowedTools` | No | 차단할 도구 |
| `model` | No | `sonnet`, `opus`, `haiku`, `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | 최대 턴 수 |
| `skills` | No | 로드할 스킬 목록 |
| `memory` | No | 영속 메모리: `user`, `project`, `local` |
| `hooks` | No | 라이프사이클 훅 |

## 활용 패턴

### 1. 고볼륨 작업 격리
테스트 실행, 로그 분석 등 대량 출력을 서브에이전트에 위임하여 메인 컨텍스트 보존

### 2. 병렬 리서치
독립적인 조사를 여러 서브에이전트에 동시 위임:
```
Research the authentication, database, and API modules in parallel using separate subagents
```

### 3. 체인 서브에이전트
순차적 워크플로우:
```
Use the code-reviewer subagent to find performance issues,
then use the optimizer subagent to fix them
```

## 예시: TestAgent + CodeAgent 워크플로우

### test-agent.md (`.claude/agents/test-agent.md`)
```markdown
---
name: test-agent
description: Write and run tests for the codebase. Use proactively when tests need to be created or updated.
tools: Read, Grep, Glob, Bash, Write, Edit
model: sonnet
---

You are a test specialist for a FastAPI + SQLAlchemy application.

When invoked:
1. Analyze the code that needs testing
2. Write pytest tests following existing patterns in backend/tests/
3. Run tests with `pytest -xvs`
4. Fix any failures
5. Report results

Testing conventions:
- Use the `client` fixture from conftest.py
- Test both success and error cases
- Use descriptive test function names
```

### code-agent.md (`.claude/agents/code-agent.md`)
```markdown
---
name: code-agent
description: Implement code changes to pass failing tests. Use after test-agent has written tests.
tools: Read, Grep, Glob, Bash, Write, Edit
model: sonnet
---

You are a code implementation specialist for a FastAPI + SQLAlchemy application.

When invoked:
1. Read the failing tests to understand requirements
2. Implement the minimum code to pass all tests
3. Run tests to verify
4. Ensure code follows existing patterns (black, ruff, 100 char line length)
5. Report what was implemented
```

## 핵심 팁
- 서브에이전트는 다른 서브에이전트를 생성할 수 없음
- `description`을 상세하게 작성해야 Claude가 적절히 위임
- 도구 접근을 최소한으로 제한하여 보안/집중도 향상
- 프로젝트 서브에이전트는 `.claude/agents/`에 넣고 버전 관리에 체크인
