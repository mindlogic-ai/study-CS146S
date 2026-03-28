# CLAUDE.md 가이던스 파일 조사

> 출처: https://code.claude.com/docs/en/claude-md (리다이렉트됨)
> 및 과제 assignment.md 내 설명

## 개요
- `CLAUDE.md`는 Claude Code 세션 시작 시 자동으로 읽히는 지침 파일
- 레포지토리/프로젝트별 지침, 컨텍스트, 가이드라인을 제공
- 프롬프트처럼 반복 개선(iterate) 가능

## 배치 위치 및 우선순위

| 위치 | 범위 |
|------|------|
| 프로젝트 루트 `CLAUDE.md` | 전체 프로젝트 |
| 서브디렉토리 `CLAUDE.md` | 해당 디렉토리 작업 시 |
| `~/.claude/CLAUDE.md` | 모든 프로젝트 (개인) |

## 포함할 내용 (과제 예시 기준)

### 1. 코드 네비게이션 & 엔트리 포인트
```markdown
## App Structure
- Entry point: `backend/app/main.py`
- Routers: `backend/app/routers/` (notes.py, action_items.py)
- Models: `backend/app/models.py` (Note, ActionItem)
- Schemas: `backend/app/schemas.py` (Pydantic v2)
- Services: `backend/app/services/extract.py`
- Tests: `backend/tests/` (conftest.py, test_*.py)
- Frontend: `frontend/` (index.html, app.js, styles.css)
- Database: `data/app.db` (SQLite), `data/seed.sql`
```

### 2. 스타일 & 안전 가드레일
```markdown
## Code Style
- Formatter: black (line length 100)
- Linter: ruff (rules: E, F, I, UP, B)
- Always run `make format` then `make lint` after changes
- Safe commands: make run, make test, make format, make lint, make seed
- Avoid: rm -rf, DROP TABLE, any destructive commands

## Testing
- Always run `make test` after code changes
- Tests use temp SQLite DB (conftest.py fixture)
- Add tests for new endpoints in backend/tests/
```

### 3. 워크플로우 스니펫
```markdown
## Workflow: Adding a New Endpoint
1. Write a failing test in backend/tests/test_*.py
2. Add Pydantic schema in backend/app/schemas.py
3. Implement the route in backend/app/routers/*.py
4. Run `make test` to verify
5. Run `make format && make lint` to clean up
6. Update frontend/app.js if UI changes needed

## Workflow: Database Changes
1. Update models in backend/app/models.py
2. Update seed.sql if needed
3. Delete data/app.db and run `make seed`
4. Update schemas.py to match
5. Run `make test`
```

## Best Practices
- 간결하고 액션 가능하게 작성
- 프롬프트처럼 반복 개선
- Claude가 사용할 커스텀 도구/스크립트 문서화
- 과도한 정보 넣지 않기 (핵심만)
- 코드 스타일, 패턴, 금지사항 명시
