# 프론트엔드 & 설정 파일 분석

## 프론트엔드 구조

### frontend/index.html
- 심플한 HTML 구조: Notes 섹션 + Action Items 섹션
- Notes: title/content 입력 폼 + 목록 (`<ul id="notes">`)
- Action Items: description 입력 폼 + 목록 (`<ul id="actions">`)
- `/static/styles.css`와 `/static/app.js` 로드

### frontend/app.js
- Vanilla JS (프레임워크 없음)
- `fetchJSON(url, options)`: 공통 API 호출 헬퍼
- `loadNotes()`: GET /notes/ → `<ul id="notes">`에 렌더링
- `loadActions()`: GET /action-items/ → `<ul id="actions">`에 렌더링
  - 미완료 항목에 "Complete" 버튼 표시
  - 클릭 시 PUT /action-items/{id}/complete 호출
- DOMContentLoaded에서 폼 submit 이벤트 바인딩
- **누락 기능**: 검색 UI, 수정/삭제 UI, 에러 처리 UI

### frontend/styles.css
- 미니멀한 CSS (9줄)
- system-ui 폰트, 900px 최대 너비
- form은 flex 레이아웃, gap 0.5rem
- 기본적인 input/button 스타일

## 설정 파일

### pyproject.toml (프로젝트 루트)
```
[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = ["E501", "B008"]
```

**주요 의존성:**
- python >= 3.10
- fastapi >= 0.111.0
- sqlalchemy >= 2.0.0
- pydantic >= 2.0.0
- google-genai >= 1.0.0

**개발 의존성:**
- pytest >= 7.0.0
- httpx >= 0.24.0
- black >= 24.1.0
- ruff >= 0.4.0
- pre-commit >= 3.6.0

### Makefile
```makefile
run:   PYTHONPATH=. uvicorn backend.app.main:app --reload
test:  PYTHONPATH=. pytest -q backend/tests
format: black . && ruff check . --fix
lint:  ruff check .
seed:  PYTHONPATH=. python -c "from backend.app.db import ..."
```

### backend/app/db.py
- SQLite 사용 (`./data/app.db`)
- `DATABASE_PATH` 환경변수로 경로 설정 가능
- `get_db()`: 의존성 주입용 세션 제너레이터
- `get_session()`: 컨텍스트 매니저 버전
- `apply_seed_if_needed()`: DB 없으면 seed.sql 적용

## TDD 자동화에 필요한 정보
- 테스트는 `backend/tests/` 에 위치
- `conftest.py`의 `client` fixture 사용 (임시 SQLite)
- `PYTHONPATH=.`로 실행해야 함
- 새 엔드포인트 추가 시: schemas.py → routers/*.py → tests/test_*.py 순서

## CLAUDE.md 동기화에 필요한 정보
- 모든 라우터 파일에서 엔드포인트 추출 가능
- pyproject.toml에서 코드 스타일 설정 추출 가능
- Makefile에서 개발 명령어 추출 가능
- models.py에서 DB 스키마 추출 가능
