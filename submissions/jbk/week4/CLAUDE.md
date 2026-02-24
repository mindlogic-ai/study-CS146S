# CLAUDE.md — Week 4 Starter App

## Project Overview
"Modern Software Dev Starter (Week 4)" — FastAPI + SQLAlchemy + SQLite 기반의 노트 및 액션 아이템 관리 앱. 프론트엔드는 정적 HTML/JS/CSS로 FastAPI에서 서빙.

## Quick Commands
```bash
make run      # uvicorn 서버 시작 (http://localhost:8000, API docs: /docs)
make test     # PYTHONPATH=. pytest -q backend/tests
make format   # black . && ruff check . --fix
make lint     # ruff check .
make seed     # SQLite DB 초기 시드 데이터 삽입
```

## Architecture
```
backend/
  app/
    main.py              # FastAPI 앱 진입점, 라우터 등록, 정적 파일 마운트
    db.py                # SQLAlchemy 엔진/세션, 시드 로직 (SQLite)
    models.py            # ORM 모델: Note, ActionItem
    schemas.py           # Pydantic v2 스키마: NoteCreate, NoteUpdate, NoteRead, ActionItemCreate, ActionItemRead
    routers/
      notes.py           # Notes CRUD 엔드포인트 (list, create, search, get, update, delete)
      action_items.py    # Action items 엔드포인트 (list, create, complete)
    services/
      extract.py         # 텍스트 → 액션 아이템 추출 유틸리티 (! 또는 TODO: 접두어 기반)
  tests/
    conftest.py          # client fixture (TestClient + 임시 SQLite DB)
    test_notes.py        # Notes 테스트 (CRUD + error cases, 6 tests)
    test_action_items.py # Action items 테스트
    test_extract.py      # extract 서비스 테스트
frontend/
  index.html             # 메인 페이지 (Notes, Action Items 섹션)
  app.js                 # API 호출 로직 (CRUD + 인라인 편집 + 삭제)
  styles.css             # 스타일
data/
  seed.sql               # 초기 시드 데이터
  app.db                 # SQLite 데이터베이스
```

## API Endpoints

| Method | Path | Function | Response Model | Status |
|--------|------|----------|----------------|--------|
| GET | `/` | `root` | FileResponse | 200 |
| GET | `/notes/` | `list_notes` | `list[NoteRead]` | 200 |
| POST | `/notes/` | `create_note` | `NoteRead` | 201 |
| GET | `/notes/search/` | `search_notes` | `list[NoteRead]` | 200 |
| GET | `/notes/{note_id}` | `get_note` | `NoteRead` | 200 |
| PUT | `/notes/{note_id}` | `update_note` | `NoteRead` | 200 |
| DELETE | `/notes/{note_id}` | `delete_note` | `{"ok": true}` | 200 |
| GET | `/action-items/` | `list_items` | `list[ActionItemRead]` | 200 |
| POST | `/action-items/` | `create_item` | `ActionItemRead` | 201 |
| PUT | `/action-items/{item_id}/complete` | `complete_item` | `ActionItemRead` | 200 |

## Data Models

### Note (`notes` 테이블)
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary key, indexed |
| title | String(200) | Not null |
| content | Text | Not null |

### ActionItem (`action_items` 테이블)
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary key, indexed |
| description | Text | Not null |
| completed | Boolean | Default false, not null |

## Schemas
- **NoteCreate** — `{title: str, content: str}`
- **NoteUpdate** — `{title: str | None, content: str | None}` (부분 수정 지원)
- **NoteRead** — `{id: int, title: str, content: str}` (from_attributes=True)
- **ActionItemCreate** — `{description: str}`
- **ActionItemRead** — `{id: int, description: str, completed: bool}` (from_attributes=True)

## Frontend Features
- **Notes**: 생성(POST), 목록 조회(GET), 인라인 편집(PUT), 삭제(DELETE)
- **Action Items**: 생성(POST), 목록 조회(GET), 완료 처리(PUT)
- `fetchJSON()` 범용 fetch 래퍼로 모든 API 호출 처리
- 인라인 편집: Edit 클릭 → input 필드로 변환 → Save/Cancel

## Code Style
- **Formatter:** black (line-length: 100, target: py310/py311/py312)
- **Linter:** ruff (line-length: 100, rules: E, F, I, UP, B, ignore: E501, B008)
- **Python:** >=3.10, <4.0 (3.12 권장)

## Testing
- **Framework:** pytest + httpx TestClient
- **현재 상태:** 8 tests passing
- **Fixture:** `client` — 테스트마다 임시 SQLite DB 생성, `get_db` 의존성 오버라이드
- **실행:** `make test`

## Development Workflow
1. 환경 설정: `conda activate cs146s && poetry install --no-interaction`
2. DB 시드: `make seed`
3. 서버 실행: `make run` → http://localhost:8000
4. 테스트: `make test`
5. 포맷/린트: `make format && make lint`
