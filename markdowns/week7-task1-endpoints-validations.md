# Task 1: Add More Endpoints and Validations

## Goal
API 엔드포인트 추가 + 입력 검증/에러 처리 강화

## Current State
**Notes 라우터:** GET /, POST /, PATCH /{id}, GET /{id}
**Action Items 라우터:** GET /, POST /, PUT /{id}/complete, PATCH /{id}

## Missing / To Add

### 1. 누락된 엔드포인트
- **DELETE /notes/{note_id}** — 노트 삭제 (204 No Content)
- **GET /action-items/{item_id}** — 단일 action item 조회
- **DELETE /action-items/{item_id}** — action item 삭제 (204 No Content)

### 2. 입력 검증 (Pydantic)
- `NoteCreate.title`: 빈 문자열 불가, max 200자 (DB Column과 일치)
- `NoteCreate.content`: 빈 문자열 불가
- `NotePatch.title`: 제공 시 빈 문자열 불가, max 200자
- `ActionItemCreate.description`: 빈 문자열 불가
- `ActionItemPatch.description`: 제공 시 빈 문자열 불가

### 3. 에러 처리
- `skip` 음수 방지: `Query(0, ge=0)`
- `limit` 범위: `Query(50, ge=1, le=200)`
- 잘못된 `sort` 필드 시 400 에러 반환 (현재는 fallback으로 조용히 넘어감)

## Files to Change
| File | Changes |
|------|---------|
| `backend/app/schemas.py` | Field 검증 추가 (min_length, max_length) |
| `backend/app/routers/notes.py` | DELETE 엔드포인트, skip/limit/sort 검증 |
| `backend/app/routers/action_items.py` | GET /{id}, DELETE 엔드포인트, skip/limit/sort 검증 |

## Test Cases
- DELETE note → 204, 이후 GET → 404
- DELETE action item → 204, 이후 GET → 404
- GET /action-items/{id} → 200, 없으면 404
- POST note with empty title → 422
- POST note with title > 200 chars → 422
- POST action item with empty description → 422
- GET /notes?skip=-1 → 422
- GET /notes?sort=nonexistent → 400

## Risks
- 기존 테스트가 깨지지 않는지 확인 필요
