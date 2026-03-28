# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Jeongbin Kim** \
SUNet ID: **jbk** \
Citations: **[Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices), [SubAgents overview](https://docs.anthropic.com/en/docs/claude-code/sub-agents)**

This assignment took me about **3** hours to do.


## YOUR RESPONSES
### Automation #1: AI-Driven TDD (`/tdd`)
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> [SubAgents overview](https://docs.anthropic.com/en/docs/claude-code/sub-agents) 문서에서 role-specialized agent 패턴을 참고했다. TDD의 Red-Green-Refactor 사이클이 자연스럽게 에이전트 역할 분리에 매핑된다: test-agent(Red)와 code-agent(Green)이 각각 독립된 컨텍스트에서 작업하고, 메인 에이전트가 오케스트레이션한다. [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)에서 slash command의 `$ARGUMENTS`로 유연한 입력을 받는 패턴과, `disable-model-invocation: true`로 수동 실행만 허용하는 안전 패턴을 적용했다.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** 기능 설명 하나로 TDD 전체 사이클을 자동화한다.
>
> **구성 파일:**
> - `.claude/commands/tdd.md` — 오케스트레이터 슬래시 커맨드
> - `.claude/agents/test-agent.md` — 테스트 작성 전문 SubAgent (model: sonnet, tools: Read/Grep/Glob/Bash/Write/Edit)
> - `.claude/agents/code-agent.md` — 구현 전문 SubAgent (동일 도구)
>
> **Input:** `$ARGUMENTS` — 구현할 기능 설명 (예: "Add PUT /notes/{id} to update a note")
>
> **Output:** 통과하는 테스트 + 구현 코드 + TDD 리포트
>
> **Steps:**
> 1. **SEARCH** — Explore agent로 코드베이스 탐색 (기존 패턴 파악). 필요 시 WebSearch로 외부 문서 조사. 병렬 실행.
> 2. **PLAN** — Search 결과를 바탕으로 수정 파일, 스키마, 엔드포인트, 테스트 케이스 계획 수립. 사용자 확인 후 진행.
> 3. **RED** — test-agent SubAgent가 실패하는 테스트 작성. `pytest -x`로 실패 확인.
> 4. **GREEN** — code-agent SubAgent가 테스트 통과하는 최소 코드 구현. `pytest`로 전체 통과 확인.
> 5. **REFACTOR** — `black` + `ruff`로 코드 정리.
> 6. **Report** — 작성한 테스트, 변경된 코드, 테스트 결과 요약 출력.
>
> **SubAgent 설계 포인트:**
> - 각 agent는 별도 컨텍스트 윈도우에서 실행되어 메인 컨텍스트를 절약한다
> - test-agent는 production 코드를 수정하지 않고, code-agent는 테스트 코드를 수정하지 않는다 (관심사 분리)
> - 둘 다 sonnet 모델을 사용하여 비용 효율적으로 운영한다

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **실행:**
> ```
> /tdd Add PUT /notes/{id} to update a note and DELETE /notes/{id} to delete a note
> ```
>
> **Expected output:**
> 1. SEARCH 결과 — 코드베이스 패턴 요약
> 2. PLAN — 수정 파일, 스키마, 엔드포인트, 테스트 케이스 목록 (사용자 확인 대기)
> 3. RED — 실패 테스트 목록 + `405 Method Not Allowed` 에러 메시지
> 4. GREEN — `8 passed, 0 failed`
> 5. REFACTOR — `All checks passed!`
> 6. Report — TDD 리포트 테이블
>
> **Rollback:** 모든 변경이 로컬 파일 수정이므로 `git checkout -- .`으로 원복 가능. 자동 커밋하지 않음.
>
> **Safety:** `disable-model-invocation: true`로 수동 실행만 가능. SubAgent는 네트워크/git 접근 없이 파일 수정만 수행.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (수동):**
> 1. 개발자가 기존 코드 읽고 패턴 파악 (~5분)
> 2. 테스트 파일 열고 테스트 케이스 수동 작성 (~10분)
> 3. pytest로 실패 확인
> 4. schemas.py, routers/notes.py 등 수동 구현 (~15분)
> 5. pytest로 통과 확인, 실패 시 디버깅 반복
> 6. black/ruff 수동 실행
> 7. 총 ~30분, 테스트 커버리지는 개발자 역량에 의존
>
> **After (자동):**
> 1. `/tdd Add PUT /notes/{id}...` 한 줄 입력
> 2. Search → Plan (사용자 확인) → Red → Green → Refactor 자동 진행
> 3. 총 ~3분, happy path + error case + edge case 자동 커버
> 4. Plan 단계에서 사용자가 방향을 확인하므로 잘못된 구현 방지

e. How you used the automation to enhance the starter application
> `/tdd Add PUT /notes/{id} to update a note and DELETE /notes/{id} to delete a note` 실행으로 TASKS.md #5 (Notes CRUD enhancements)를 구현했다.
>
> **Search 단계:** Explore agent가 기존 notes.py, action_items.py, schemas.py, conftest.py의 패턴을 분석하고 수정 필요 파일을 정리.
>
> **Plan 단계:** NoteUpdate 스키마(Optional 필드), PUT/DELETE 엔드포인트 설계, 테스트 5개(부분 수정, 전체 수정, 404 에러 2개, 삭제 확인)를 계획. 사용자 승인 후 진행.
>
> **Red 단계:** test-agent가 5개 테스트 작성 → `405 Method Not Allowed`로 실패 확인.
>
> **Green 단계:** code-agent가 NoteUpdate 스키마 + PUT/DELETE 라우트 구현 → 8 tests passed.
>
> **결과:** 기존 3개 테스트에서 8개로 확장, API 엔드포인트 7개 → 9개로 증가.


### Automation #2: CLAUDE.md Sync (`/sync-claude-md`)
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)에서 CLAUDE.md를 "프로젝트의 진실의 원천(source of truth)"으로 유지하라는 가이드를 참고했다. 문서가 코드와 동기화되지 않으면 오히려 해롭다는 점에서, 코드베이스를 직접 분석해서 CLAUDE.md를 자동 생성하는 자동화를 설계했다. Slash command의 단계별 워크플로우 구성은 best practices의 "focused, idempotent steps" 원칙을 따랐다.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** 코드베이스의 실제 상태를 분석하여 CLAUDE.md를 자동 생성/업데이트한다.
>
> **구성 파일:** `.claude/commands/sync-claude-md.md`
>
> **Input:** 없음 (코드베이스에서 직접 읽음)
>
> **Output:** 업데이트된 `CLAUDE.md` + 변경 리포트
>
> **Steps:**
> 1. **Analyze Structure** — `backend/app/`, `backend/tests/`, `frontend/`, config 파일 탐색
> 2. **Extract Endpoints** — 라우터 파일에서 HTTP method, path, function, response model, status code 추출
> 3. **Extract Code Style** — `pyproject.toml`에서 black/ruff 설정 추출
> 4. **Extract Commands** — `Makefile`에서 개발 명령어 추출
> 5. **Check Tests** — `pytest -q` 실행하여 테스트 수/결과 확인
> 6. **Generate CLAUDE.md** — 위 정보를 종합하여 9개 섹션(Overview, Commands, Architecture, Endpoints, Models, Schemas, Code Style, Testing, Workflow)으로 구성된 CLAUDE.md 작성
> 7. **Report** — 문서화된 엔드포인트 수, 모델 수, 불일치 사항 출력

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **실행:**
> ```
> /sync-claude-md
> ```
>
> **Expected output:**
> 1. 프로젝트 구조 분석 결과
> 2. API 엔드포인트 테이블 (Method, Path, Function, Response Model, Status)
> 3. pyproject.toml 코드 스타일 설정
> 4. Makefile 명령어 목록
> 5. 테스트 결과 (예: "8 passed, 0 failed")
> 6. 생성된 CLAUDE.md 내용
> 7. Sync Report 테이블 (섹션 수, 엔드포인트 수, 모델 수, 불일치 여부)
>
> **Rollback:** `git checkout -- CLAUDE.md`로 원복. 단일 파일만 수정.
>
> **Safety:** `disable-model-invocation: true`로 수동 실행만 가능. 읽기 위주 작업이며, CLAUDE.md 외 파일은 수정하지 않음.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (수동):**
> 1. 개발자가 새 엔드포인트 추가
> 2. CLAUDE.md 또는 API 문서 업데이트를 잊음 (또는 불일치하게 수정)
> 3. 시간이 지나면서 문서와 코드가 점점 벌어짐
> 4. 새 개발자(또는 Claude)가 오래된 문서를 보고 혼란
>
> **After (자동):**
> 1. 기능 추가 후 `/sync-claude-md` 실행
> 2. 코드에서 직접 엔드포인트, 모델, 테스트 현황을 추출
> 3. CLAUDE.md가 항상 코드의 실제 상태와 일치
> 4. Claude가 정확한 프로젝트 컨텍스트를 갖고 작업 가능

e. How you used the automation to enhance the starter application
> `/sync-claude-md`를 2번 실행하여 Before/After를 확인했다.
>
> **1차 실행 (기능 추가 전):** 스타터 앱 초기 상태를 분석. 7개 엔드포인트, 2개 모델, 4개 스키마, 3개 테스트를 문서화한 CLAUDE.md 생성.
>
> **2차 실행 (`/tdd` 후):** PUT/DELETE 추가 후 재실행하면 CLAUDE.md가 자동 업데이트됨:
> - API Endpoints 테이블: 7개 → 9개 (PUT /notes/{id}, DELETE /notes/{id} 추가)
> - Schemas: NoteUpdate 스키마 추가 반영
> - Testing: 3 tests → 8 tests로 업데이트
>
> 이로써 `/tdd`로 기능을 추가하고 `/sync-claude-md`로 문서를 동기화하는 **개발-문서화 파이프라인**이 완성되었다.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> N/A

b. Design of each automation, including goals, inputs/outputs, steps
> N/A

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> N/A

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> N/A

e. How you used the automation to enhance the starter application
> N/A
