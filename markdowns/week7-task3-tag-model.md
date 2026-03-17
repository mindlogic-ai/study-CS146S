# Task 3: Add Tag Model and Relationships

## Goal
Tag 모델을 추가하고 Note와 many-to-many 관계 설정

## Changes

### 1. 모델
- `Tag` 모델: id, name (unique, max 50), timestamps
- `note_tags` association table (note_id, tag_id) with CASCADE delete

### 2. 관계
- `Note.tags` ↔ `Tag.notes` many-to-many, lazy="selectin"

### 3. 스키마
- `TagCreate(name)`, `TagRead(id, name, created_at, updated_at)`
- `NoteRead`에 `tags: list[TagRead]` 추가

### 4. 엔드포인트 (tags router)
- GET /tags/ — 전체 목록
- POST /tags/ — 생성 (201, 중복 시 409)
- DELETE /tags/{id} — 삭제 (204, 404)

### 5. Note-Tag 연결 엔드포인트
- POST /notes/{note_id}/tags/{tag_id} — 태그 연결 (idempotent)
- DELETE /notes/{note_id}/tags/{tag_id} — 태그 해제

## Files to Change
| File | Changes |
|------|---------|
| `backend/app/models.py` | Tag, note_tags, relationship |
| `backend/app/schemas.py` | TagCreate, TagRead, NoteRead 수정 |
| `backend/app/routers/tags.py` | 새 라우터 |
| `backend/app/routers/notes.py` | attach/detach 엔드포인트 |
| `backend/app/main.py` | tags router 등록 |
| `backend/tests/test_tags.py` | 테스트 |
