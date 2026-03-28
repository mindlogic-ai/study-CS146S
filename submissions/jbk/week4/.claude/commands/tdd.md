---
disable-model-invocation: true
---

# AI-Driven TDD Workflow

You are running an AI-driven TDD (Test-Driven Development) workflow for the following feature request:

**Feature:** $ARGUMENTS

## Workflow Steps

### Step 1: SEARCH — 리서치 (코드베이스 + 외부 지식)
기능 구현에 필요한 모든 정보를 수집한다. 두 가지를 병렬로 진행:

**1a. 코드베이스 탐색** — Explore agent로 기존 코드 파악:
```
Launch Task(subagent_type=Explore) with prompt:
"다음 기능을 구현하기 위해 코드베이스를 탐색해줘: $ARGUMENTS

조사할 것:
1. backend/app/routers/ — 기존 엔드포인트 패턴 (데코레이터, 파라미터, 에러처리)
2. backend/app/schemas.py — 기존 스키마 패턴 (필드 타입, 검증, Config)
3. backend/app/models.py — 관련 모델 구조 (컬럼, 타입, 제약조건)
4. backend/tests/ — 기존 테스트 패턴 (fixture, assert 스타일)
5. backend/app/services/ — 비즈니스 로직 패턴
6. pyproject.toml 또는 requirements — 현재 설치된 라이브러리

각 파일의 핵심 패턴을 요약하고, 새 기능이 어떤 파일을 수정해야 하는지 정리해줘."
```

**1b. 외부 리서치** — 기능 구현에 필요한 외부 지식 조사 (필요한 경우에만):
- 새 라이브러리/패턴이 필요한 경우 → WebSearch로 공식 문서, 사용법, 베스트 프랙티스 검색
- 익숙하지 않은 기술 스택인 경우 → WebFetch로 공식 문서 읽기
- 비슷한 구현 사례가 필요한 경우 → WebSearch로 참고 코드 검색

예시:
- "Add WebSocket" → FastAPI WebSocket 공식 문서 검색
- "Add OAuth login" → OAuth2 + FastAPI 통합 패턴 검색
- "Add pagination" → 기존 코드만으로 충분하면 외부 리서치 생략

**1a와 1b는 병렬로 실행하여 시간을 절약한다.**

### Step 2: PLAN — 구현 계획 수립
Search 결과를 바탕으로 구현 계획을 세운다:

1. **수정할 파일 목록** — 어떤 파일에 뭘 추가/변경할지
2. **스키마 설계** — 필요한 Request/Response 스키마
3. **엔드포인트 설계** — HTTP method, path, status code, 에러 케이스
4. **테스트 케이스 목록** — 성공/실패/엣지 케이스별 테스트 시나리오

이 계획을 사용자에게 보여주고 확인받은 후 다음 단계로 진행한다.

### Step 3: RED — Write Failing Tests First
Use the **test-agent** SubAgent to write tests:

```
Launch SubAgent "test-agent" with prompt:
"Write failing tests for: $ARGUMENTS

Context:
- Tests go in backend/tests/
- Use the `client` fixture from conftest.py (TestClient with temp SQLite DB)
- Follow existing test patterns in test_notes.py and test_action_items.py
- Cover: success cases, error cases (404, 422), edge cases
- Run tests with: PYTHONPATH=. pytest -q backend/tests/ — they should FAIL"
```

After the test-agent completes, verify the tests fail by running:
```bash
PYTHONPATH=. pytest -q backend/tests/ -x
```

Report which tests fail and why (this is expected — RED phase).

### Step 4: GREEN — Implement Minimum Code to Pass
Use the **code-agent** SubAgent to implement:

```
Launch SubAgent "code-agent" with prompt:
"Implement the minimum code to make all tests pass for: $ARGUMENTS

Context:
- Follow existing patterns in the codebase
- Add schemas to backend/app/schemas.py if needed
- Add/modify routes in backend/app/routers/
- Add/modify models in backend/app/models.py if needed
- Run tests with: PYTHONPATH=. pytest -q backend/tests/ — they should ALL PASS
- Format code with: black . && ruff check . --fix"
```

After the code-agent completes, verify all tests pass:
```bash
PYTHONPATH=. pytest -q backend/tests/
```

### Step 5: REFACTOR — Clean Up
Review the implementation and tests:
- Ensure code follows black (100 char line length) and ruff standards
- Remove any duplication
- Run final checks:
```bash
black . && ruff check . --fix
PYTHONPATH=. pytest -q backend/tests/
```

### Step 6: Report
Output a summary in this format:

```
## TDD Report: $ARGUMENTS

### Tests Written
- [list each test function and what it tests]

### Code Changes
- [list each file modified and what changed]

### Test Results
- Total: X passed, 0 failed
- All tests passing ✓

### Files Modified
- [list all files touched]
```
