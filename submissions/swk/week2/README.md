# Week 2 — Action Item Extractor

자유 형식 노트에서 액션 아이템(할 일 목록)을 자동 추출하는 FastAPI + SQLite 웹 애플리케이션입니다.

## 프로젝트 개요

사용자가 입력한 텍스트에서 할 일 항목을 자동으로 추출하고, 체크리스트 형태로 관리할 수 있습니다.

**주요 기능:**
- 노트 저장 및 조회
- 규칙 기반 액션 아이템 추출 (불릿, 체크박스, 키워드 접두사)
- LLM 기반 액션 아이템 추출 (Google Gemini API)
- 액션 아이템 완료 상태 토글

## 기술 스택

- **Backend:** FastAPI, SQLite
- **Frontend:** Vanilla JavaScript (Single Page)
- **LLM:** Google Gemini API

## 설정 및 실행

### 사전 요구사항

- Python 3.10+
- Conda 환경 (`cs146s`)
- Poetry
- Google Gemini API 키 (LLM 기능 사용 시)

### 설치

```bash
# Conda 환경 활성화
conda activate cs146s

# 의존성 설치
poetry install
```

### 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Gemini API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 발급받을 수 있습니다.

### 서버 실행

```bash
# 프로젝트 루트에서 실행
poetry run uvicorn week2.app.main:app --reload
```

브라우저에서 http://127.0.0.1:8000/ 접속

## API 엔드포인트

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | 새 노트 생성 |
| `GET` | `/notes` | 모든 노트 조회 |
| `GET` | `/notes/{note_id}` | 특정 노트 조회 |

**POST /notes**
```json
// Request
{ "content": "노트 내용" }

// Response
{ "id": 1, "content": "노트 내용", "created_at": "2024-..." }
```

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | 규칙 기반 액션 아이템 추출 |
| `POST` | `/action-items/extract-llm` | LLM 기반 액션 아이템 추출 |
| `GET` | `/action-items` | 액션 아이템 목록 조회 |
| `POST` | `/action-items/{id}/done` | 완료 상태 토글 |

**POST /action-items/extract**
```json
// Request
{ "text": "- 회의 준비\n- 보고서 작성", "save_note": true }

// Response
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "회의 준비" },
    { "id": 2, "text": "보고서 작성" }
  ]
}
```

**POST /action-items/extract-llm**
```json
// Request
{ "text": "내일까지 보고서 완성하고 팀장님께 검토 요청하기", "save_note": true }

// Response
{
  "note_id": 2,
  "items": [
    { "id": 3, "text": "보고서 완성" },
    { "id": 4, "text": "팀장님께 검토 요청" }
  ]
}
```

## 액션 아이템 추출 로직

### 규칙 기반 추출 (`extract_action_items`)

1. **패턴 매칭 (1차)**
   - 불릿 포인트: `- * •` 또는 `1.` 형식
   - 키워드 접두사: `todo:`, `action:`, `next:`
   - 체크박스: `[ ]`, `[todo]`

2. **명령형 문장 감지 (2차, 패턴 없을 시)**
   - 동사로 시작하는 문장 추출
   - 지원 동사: add, create, implement, fix, update, write, check, verify, refactor, document, design, investigate

### LLM 기반 추출 (`extract_action_items_llm`)

- Google Gemini API를 통해 LLM 호출
- 구조화된 JSON 출력으로 액션 아이템 배열 반환
- 자연어 문맥 이해 기반 추출

## 프로젝트 구조

```
week2/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── db.py                # SQLite 데이터베이스 레이어
│   ├── routers/
│   │   ├── notes.py         # 노트 API 라우터
│   │   └── action_items.py  # 액션 아이템 API 라우터
│   └── services/
│       └── extract.py       # 추출 로직 (규칙 기반 + LLM)
├── frontend/
│   └── index.html           # 프론트엔드 SPA
├── tests/
│   └── test_extract.py      # 유닛 테스트
├── data/
│   └── app.db               # SQLite 데이터베이스 파일
└── README.md
```

## 데이터베이스 스키마

### notes 테이블
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| content | TEXT | 노트 내용 |
| created_at | TEXT | 생성 시각 |

### action_items 테이블
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| note_id | INTEGER | 노트 FK (nullable) |
| text | TEXT | 액션 아이템 내용 |
| done | INTEGER | 완료 여부 (0/1) |
| created_at | TEXT | 생성 시각 |

## 테스트 실행

```bash
# 프로젝트 루트에서 실행
poetry run pytest week2/tests/ -v
```

### 테스트 케이스

- 불릿 포인트 추출 테스트
- 체크박스 형식 추출 테스트
- 빈 입력 처리 테스트
- LLM 추출 테스트 (Gemini API 키 필요)

## 프론트엔드 사용법

1. 텍스트 영역에 노트 입력
2. "Save as note" 체크박스로 노트 저장 여부 선택
3. **Extract** 버튼: 규칙 기반 추출
4. **Extract LLM** 버튼: LLM 기반 추출
5. **List Notes** 버튼: 저장된 노트 목록 조회
6. 추출된 항목 체크박스 클릭으로 완료 상태 변경
