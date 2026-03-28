# 스타터 앱 코드 분석

## 아키텍처
```
FastAPI → Routers → Services → SQLAlchemy Models
                 ↓
            Pydantic Schemas
```

## 핵심 파일

### backend/app/main.py
- FastAPI 앱 생성 (`title="Modern Software Dev Starter (Week 4)"`)
- `frontend/` 디렉토리를 `/static`에 마운트
- startup 이벤트에서 테이블 생성 + seed 적용
- `/` 루트 → `frontend/index.html` 서빙
- notes, action_items 라우터 등록

### backend/app/models.py
```python
class Note(Base):            # notes 테이블
    id: Integer (PK)
    title: String(200)
    content: Text

class ActionItem(Base):      # action_items 테이블
    id: Integer (PK)
    description: Text
    completed: Boolean (default=False)
```

### backend/app/schemas.py
```python
NoteCreate(title: str, content: str)
NoteRead(id: int, title: str, content: str)
ActionItemCreate(description: str)
ActionItemRead(id: int, description: str, completed: bool)
```
- `from_attributes = True` (Pydantic v2)

### backend/app/routers/notes.py
- `GET /notes/` - 전체 노트 목록
- `POST /notes/` - 노트 생성 (201)
- `GET /notes/search/?q=...` - 제목/내용 검색 (contains)
- `GET /notes/{note_id}` - 단일 노트 조회 (404 처리)
- **누락**: PUT (수정), DELETE (삭제), PATCH 없음

### backend/app/routers/action_items.py
- `GET /action-items/` - 전체 목록
- `POST /action-items/` - 생성 (201)
- `PUT /action-items/{id}/complete` - 완료 처리 (404 처리)
- **누락**: DELETE, PATCH, uncomplete 없음

### backend/app/services/extract.py
```python
def extract_action_items(text: str) -> list[str]:
    # "!"로 끝나거나 "todo:"로 시작하는 줄 추출
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]
```
- **개선 가능**: #tag 파싱, 더 정교한 패턴 매칭

### backend/tests/
- `conftest.py`: 임시 SQLite DB + TestClient fixture
- `test_notes.py`: 생성, 목록, 검색 테스트
- `test_action_items.py`: 생성, 완료, 목록 테스트
- `test_extract.py`: extract_action_items 단위 테스트
- **누락**: 에러 케이스, 유효성 검사, 엣지 케이스 테스트

### frontend/app.js
- Vanilla JS (프레임워크 없음)
- fetchJSON 헬퍼로 API 호출
- Notes 섹션: 추가 폼, 목록 표시
- Action Items 섹션: 추가 폼, 완료 버튼

## 개선 가능 영역 (TASKS.md 기준)
1. ✅ Pre-commit 설정 (이미 config 있음, 설치만 하면 됨)
2. 🔧 검색 엔드포인트 case-insensitive로 개선
3. ✅ Action item 완료 플로우 (이미 구현됨)
4. 🔧 추출 로직 개선 (#tag, @mention 등)
5. 🔧 Notes CRUD 확장 (PUT, DELETE)
6. 🔧 요청 유효성 검사 (min length 등)
7. 🔧 API 문서 drift 체크
