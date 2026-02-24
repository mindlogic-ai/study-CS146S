# Week 4 Write-up

## SUBMISSION DETAILS

Name: **Hyungjoon** \
SUNet ID: **hjy** \
Citations:
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — 슬래시 커맨드 아이디어 탐색
- [toyamarinyon/giselle - create-pr.md](https://github.com/toyamarinyon/giselle/blob/main/.claude/commands/create-pr.md) — PR 자동화 참고
- [jerseycheese/Narraitor - create-docs.md](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/create-docs.md) — 문서 생성 참고
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code Slash Commands 공식 문서](https://code.claude.com/docs/en/slash-commands)

This assignment took me about **2** hours to do.


## YOUR RESPONSES

### Automation #1: `/create-docs` (Custom Slash Command)

a. Design inspiration
> [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) 목록에서 슬래시 커맨드 예시들을 탐색하다가 [jerseycheese/Narraitor의 create-docs](https://github.com/jerseycheese/Narraitor/blob/feature/issue-227-ai-suggestions/.claude/commands/create-docs.md)를 발견했다. 코드를 분석해서 문서를 자동 생성하는 건데, FastAPI는 OpenAPI 스펙이 내장이니까 이거랑 조합하면 쓸만하겠다 싶었다.
b. Design of each automation
> **목표:** 라우터 파일과 Pydantic 스키마를 읽어서 `docs/API.md`를 자동 생성.
>
> **입력:** `$ARGUMENTS`로 대상 지정 (예: `all`, `backend/app/routers`, 특정 파일 경로)
>
> **동작 순서:**
> 1. 라우터 파일에서 `@router.get/post/put/delete` 데코레이터 탐색
> 2. 각 엔드포인트의 HTTP method, path, 파라미터, response model, status code 추출
> 3. Pydantic 스키마 분석 — 필드명, 타입, 기본값, Field 제약조건
> 4. 기존 `docs/API.md`가 있으면 비교해서 변경점(추가/삭제/수정) 감지
> 5. 새 `docs/API.md` 생성 — 엔드포인트 테이블, 스키마 상세, 에러 코드
> 6. 변경 요약 리포트 출력
>
> **출력:** `docs/API.md` 파일 + 콘솔에 변경 요약

c. How to run it
> ```
> /create-docs all
> /create-docs backend/app/routers/notes.py
> ```
> 예상 출력: `docs/API.md`가 생성되고, "9 endpoints documented, 5 schemas found" 같은 요약 출력.
>
> **롤백:** `git checkout -- docs/API.md` 하면 원래대로 돌아감. 소스코드는 건드리지 않으므로 안전.

d. Before vs. after
> **Before:** 새 엔드포인트 추가할 때마다 수동으로 문서 업데이트. 근데 솔직히 아무도 안 함. API.md가 실제 코드랑 안 맞는 상태가 됨.
>
> **After:** `/create-docs all` 한 번이면 전체 API 문서가 코드 기반으로 갱신. 코드가 source of truth이니까 drift 걱정 없음.

e. How you used the automation to enhance the starter application
> PUT/DELETE 엔드포인트와 validation을 추가한 뒤에 `/create-docs all`을 실행했다. 결과:
>
> - **9 endpoints** 문서화 (Notes 6개 + Action Items 3개)
> - **5 schemas** 문서화 (NoteCreate, NoteUpdate, NoteRead, ActionItemCreate, ActionItemRead)
> - 각 엔드포인트별 HTTP method, path, query/path params, request body, response model, error codes 포함
> - Field 제약조건 (`min_length`, `max_length`)까지 스키마 테이블에 반영
>
> 생성된 `docs/API.md`로 TASKS.md의 Task 7 (Docs drift check)을 해결. 이후 엔드포인트를 추가하거나 스키마를 변경하면 `/create-docs all`을 다시 실행해서 문서를 갱신하면 된다.


### Automation #2: `/create-pr` (Custom Slash Command)

a. Design inspiration
> 같은 awesome-claude-code 목록에서 [toyamarinyon/giselle의 create-pr](https://github.com/toyamarinyon/giselle/blob/main/.claude/commands/create-pr.md)을 발견했다. 브랜치 만들고, 포맷하고, 커밋하고, PR 올리는 걸 한 커맨드로 하는 건데, 이게 매주 과제 제출할 때 하는 짓이라서 바로 와닿았다. [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)에서도 반복 워크플로우를 커맨드로 만들라고 했으니까.

b. Design of each automation
> **목표:** 변경사항을 분석하고, 포맷팅하고, 논리적으로 커밋을 나눠서 PR을 생성.
>
> **입력:** `$ARGUMENTS`로 PR 제목 힌트 (선택사항). 없으면 변경사항 기반으로 자동 생성.
>
> **동작 순서:**
> 1. `git status` + `git diff`로 변경사항 분석, 카테고리 분류 (feature/fix/docs/test)
> 2. 포맷터/린터 실행 (Makefile 있으면 `make format && make lint`)
> 3. 변경사항을 논리적 단위로 분리해 커밋 (conventional commit: `feat:`, `test:`, `docs:` 등)
> 4. `git push -u origin <branch>`
> 5. `gh pr create`로 PR 생성 — Summary, Changes, Test plan 포함
>
> **출력:** PR URL + 커밋 수 + 변경 요약

c. How to run it
> ```
> /create-pr [Week4 - hjy] 과제 완료
> /create-pr
> ```
> 예상 출력: PR URL, 커밋 개수, 변경된 파일 목록.
>
> **안전장치:**
> - `.env`, credentials 파일은 절대 커밋 안 함
> - force push 안 함
> - 변경 파일 10개 초과 시 확인 요청
> - merge conflict 있으면 중단하고 알려줌
>
> **롤백:** PR은 GitHub에서 close하면 됨. 로컬 커밋은 `git reset --soft HEAD~N`으로 되돌릴 수 있음.

d. Before vs. after
> **Before:** 매번 수동으로 `git add` → 커밋 메시지 고민 → `git push` → GitHub 가서 PR 생성 → 제목/본문 작성. 5분은 걸림.
>
> **After:** `/create-pr` 한 번이면 끝. 커밋도 논리적으로 나눠주고, PR 본문도 자동 생성. 특히 과제 제출할 때 편함.

e. How you used the automation to enhance the starter application
> 모든 기능 구현이 끝난 뒤에 `/create-pr [Week4 - hjy]`을 실행해서 과제 제출 PR을 만들 계획. 변경사항을 자동으로 분류해서 깔끔한 커밋 히스토리와 PR 본문을 생성해줌.


### Automation #3: `CLAUDE.md` (Project Guidance)

a. Design inspiration
> [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)에서 CLAUDE.md를 "프로젝트의 source of truth"로 쓰라고 했다. 레포 루트에 이미 전체 프로젝트용 CLAUDE.md가 있었지만, week4 서브디렉토리의 구체적인 구조와 패턴까지는 담고 있지 않아서 week4 전용 가이드를 추가했다.

b. Design of each automation
> **목표:** Claude Code가 week4의 구체적인 디렉토리 구조, 아키텍처 패턴, 코드 스타일을 이해하고 올바른 패턴으로 코드를 작성하도록 가이드.
>
> **루트 CLAUDE.md와의 차이:** 루트 CLAUDE.md는 전체 레포의 빌드 커맨드, 주차별 구조, 제출 워크플로우 등 범용 정보를 담고 있고, week4 CLAUDE.md는 이 주차의 FastAPI 앱에 특화된 정보를 담는다.
>
> **내용:**
> - Quick Start 명령어 (`make run/test/format/lint/seed`)
> - week4 프로젝트 디렉토리 구조 (각 파일의 역할 명시)
> - 아키텍처 패턴 (FastAPI Router → SQLAlchemy Model → Pydantic Schema)
> - 코드 스타일 (100자, black, ruff)
> - 테스트 패턴 (pytest + TestClient, tmp DB)
>
> **입출력:** 없음. Claude Code가 week4 디렉토리에서 세션 시작 시 자동으로 읽음.

c. How to run it
> 별도 실행 불필요. `submissions/hjy/week4/` 디렉토리에서 Claude Code를 시작하면 루트 CLAUDE.md와 함께 자동 로드.
>
> **안전:** 읽기 전용 가이드 파일이라 사이드이펙트 없음.

d. Before vs. after
> **Before:** 루트 CLAUDE.md만 있는 상태. 이 정도 규모의 프로젝트에서는 Claude가 코드를 읽으면 알아서 패턴을 파악하긴 함.
>
> **After:** week4 전용 CLAUDE.md 추가. 솔직히 이 규모에서는 드라마틱한 차이는 없다. 다만 `make` 커맨드나 테스트 실행 방법 같은 건 코드만 봐서는 알기 어렵기 때문에, 그 부분에서는 유용했다. 프로젝트가 커지면 효과가 더 클 것으로 기대.

e. How you used the automation to enhance the starter application
> PUT/DELETE 엔드포인트 구현 시 CLAUDE.md에 명시한 패턴(`db.get()`, `model_validate()`, `Depends(get_db)`)을 따르긴 했지만, 사실 기존 코드만 봐도 충분히 파악 가능한 수준이었다. CLAUDE.md가 실질적으로 도움이 된 건 `make test`, `make format` 같은 커맨드 안내와 테스트 패턴(tmp DB fixture) 부분.
