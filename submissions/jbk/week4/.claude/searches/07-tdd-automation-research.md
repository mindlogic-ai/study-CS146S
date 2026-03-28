# AI-Driven TDD 자동화 조사

## 개요
과제에서 선택할 자동화 #1: **AI-Driven TDD (Test-Driven Development) 워크플로우**
- 과제 assignment.md의 "C) SubAgents - Example 1: TestAgent + CodeAgent" 패턴 활용
- 슬래시 커맨드로 TDD 워크플로우를 트리거

## 핵심 아이디어
1. `/tdd` 슬래시 커맨드로 TDD 워크플로우 시작
2. TestAgent가 먼저 실패하는 테스트 작성
3. CodeAgent가 테스트를 통과하는 코드 구현
4. TestAgent가 최종 검증

## Best Practices 기반 설계 원칙

### Claude Code Best Practices에서 가져온 원칙
1. **"검증 수단 제공이 가장 중요"** → TDD는 검증이 내장된 워크플로우
2. **"탐색 → 계획 → 코드"** → 테스트 작성이 계획 역할
3. **"서브에이전트로 컨텍스트 보존"** → TestAgent/CodeAgent 분리
4. **Writer/Reviewer 패턴** → 테스트 작성자와 코드 구현자 분리

### SubAgents 문서에서 가져온 원칙
1. **"focused subagents"** → 각 에이전트가 하나의 역할에 집중
2. **"도구 접근 제한"** → TestAgent는 테스트만, CodeAgent는 구현만
3. **"체인 서브에이전트"** → 순차적 워크플로우 구성
4. **"description 상세 작성"** → Claude가 적절히 위임하도록

## 구현 계획

### 방법 1: 슬래시 커맨드 (`.claude/commands/tdd.md`)
```yaml
---
name: tdd
description: AI-driven TDD workflow - write failing tests first, then implement
disable-model-invocation: true
argument-hint: [feature-description]
---

AI-Driven TDD Workflow for: $ARGUMENTS

## Step 1: Analyze Requirements
- Read the feature description
- Identify the files that need to be created or modified
- Look at existing test patterns in backend/tests/

## Step 2: Write Failing Tests (Red Phase)
- Write comprehensive test cases FIRST
- Tests should cover: happy path, edge cases, error cases
- Follow existing test patterns (use `client` fixture)
- Run `make test` to confirm tests FAIL

## Step 3: Implement Code (Green Phase)
- Write minimum code to pass ALL tests
- Follow existing code patterns in backend/app/
- Run `make test` to confirm tests PASS

## Step 4: Refactor (Refactor Phase)
- Clean up code while keeping tests green
- Run `make format && make lint`
- Run `make test` one final time

## Step 5: Report
- Summary of tests written
- Summary of code implemented
- Final test results
```

### 방법 2: SubAgent 조합
test-agent.md + code-agent.md를 `.claude/agents/`에 생성하고,
슬래시 커맨드에서 이들을 체이닝하는 방식

### 추천: 방법 1 + 방법 2 결합
- 슬래시 커맨드 `/tdd`가 워크플로우 오케스트레이션
- SubAgent가 실제 작업 수행 (테스트 작성, 코드 구현)

## 스타터 앱에 적용할 수 있는 TDD 작업들 (TASKS.md 기준)
1. **Notes CRUD 확장** - PUT/DELETE 엔드포인트 추가
   - 테스트: update note, delete note, 404 에러 처리
   - 구현: routers/notes.py에 PUT, DELETE 추가
2. **요청 유효성 검사** - min length 등 validation 추가
   - 테스트: 빈 title, 빈 content 등 실패 케이스
   - 구현: schemas.py에 Field(min_length=1) 추가
3. **추출 로직 개선** - #tag 파싱
   - 테스트: #tag 포함 텍스트 추출
   - 구현: extract.py 로직 확장

## Before vs After 비교
### Before (수동 워크플로우)
1. 어떤 테스트를 써야 할지 직접 고민
2. 테스트 파일 수동 생성
3. 코드 구현
4. 테스트 실행, 실패 시 수동 디버깅
5. 포맷팅/린팅 수동 실행
→ 반복적이고 실수하기 쉬움

### After (자동화 워크플로우)
1. `/tdd "Add PUT/DELETE endpoints for notes"` 실행
2. TestAgent가 자동으로 테스트 설계 및 작성
3. CodeAgent가 테스트 통과하는 코드 자동 구현
4. 자동 검증 + 포맷팅/린팅
→ 일관성 있고 빠른 개발 사이클
