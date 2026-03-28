# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: swk \
SUNet ID: nope \
Citations: Claude

This assignment took me about 0.5 hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
TODO 1번에 gemini를 활용한 extract_action_items_llm()을 구현해

기존 extract_action_items() 함수를 분석하고, Google Gemini API를 사용하여
LLM 기반 액션 아이템 추출 함수를 구현해줘. 구조화된 JSON 출력을 사용하고,
에러 처리와 중복 제거 로직도 포함해줘.
```

Generated Code Snippets:
```
week2/app/services/extract.py (lines 94-164)

# -----------------------------------------------------------------------------
# LLM-powered extraction using Google Gemini API
# -----------------------------------------------------------------------------

def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using Google Gemini API.

    - Gemini 2.0 Flash 모델 사용
    - response_mime_type="application/json" + JSON 스키마로 구조화된 출력
    - temperature=0.1 로 일관된 추출 결과
    - 에러 발생 시 빈 배열 반환
    - 대소문자 무시 중복 제거
    """
```

### Exercise 2: Add Unit Tests
Prompt:
```
extract_action_items_llm()에 대한 유닛 테스트를 작성해줘.
다양한 입력 케이스를 커버해야 해:
- 불릿 리스트
- 키워드 접두사 (TODO:, ACTION:, NEXT:)
- 빈 입력
- 액션 아이템이 없는 텍스트
- 자연어 문장
- 체크박스 형식
- 혼합 형식
```

Generated Code Snippets:
```
week2/tests/test_extract.py (lines 22-95)

class TestExtractActionItemsLLM:
    """Unit tests for LLM-powered action item extraction using Gemini API."""

    - test_llm_extract_bullet_list: 불릿 포인트 추출 테스트
    - test_llm_extract_keyword_prefixed: 키워드 접두사 추출 테스트
    - test_llm_extract_empty_input: 빈 입력 처리 테스트
    - test_llm_extract_no_action_items: 액션 아이템 없는 텍스트 테스트
    - test_llm_extract_natural_language: 자연어 문장 추출 테스트
    - test_llm_extract_checkbox_format: 체크박스 형식 추출 테스트
    - test_llm_extract_mixed_format: 혼합 형식 추출 테스트
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
코드베이스를 리팩토링해줘:
1. Pydantic 스키마를 사용한 API 요청/응답 타입 정의
2. Dict[str, Any] 대신 명확한 타입 사용
3. FastAPI lifespan 패턴으로 앱 라이프사이클 관리
4. 적절한 HTTP 상태 코드 사용 (201 for creation)
5. response_model 지정으로 자동 문서화 개선
```

Generated/Modified Code Snippets:
```
week2/app/schemas.py (새 파일, lines 1-72)
- NoteCreate, NoteResponse: 노트 요청/응답 스키마
- ActionItemResponse, ActionItemExtract: 액션 아이템 스키마
- ExtractRequest, ExtractResponse: 추출 요청/응답 스키마
- MarkDoneRequest, MarkDoneResponse: 완료 상태 변경 스키마

week2/app/main.py (lines 22-45)
- asynccontextmanager lifespan 패턴으로 DB 초기화
- FastAPI 앱에 description, version 추가

week2/app/routers/notes.py (lines 1-70)
- Dict[str, Any] → Pydantic 스키마로 전환
- response_model 추가로 자동 문서화
- status.HTTP_201_CREATED 사용
- list_notes() 엔드포인트 추가

week2/app/routers/action_items.py (lines 1-105)
- Dict[str, Any] → Pydantic 스키마로 전환
- response_model 추가
- 독스트링 추가로 가독성 개선
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
LLM 추출 기능을 위한 새 엔드포인트와 프론트엔드 UI를 추가해줘:
1. /action-items/extract-llm POST 엔드포인트 추가
2. 프론트엔드에 "Extract LLM" 버튼 추가
3. 프론트엔드에 "List Notes" 버튼 추가
4. 버튼 클릭 핸들러 구현
```

Generated Code Snippets:
```
week2/app/routers/action_items.py (lines 48-71)
- extract_llm() 엔드포인트: LLM 기반 액션 아이템 추출
- extract_action_items_llm import 추가

week2/frontend/index.html (lines 24-30)
- "Extract LLM" 버튼 추가
- "List Notes" 버튼 추가
- notes 표시 영역 추가

week2/frontend/index.html (lines 31-87)
- renderItems() 헬퍼 함수로 중복 코드 제거
- extract-llm 버튼 클릭 핸들러 (lines 46-61)
- list-notes 버튼 클릭 핸들러 (lines 63-81)
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
week2 프로젝트를 분석하고 README.md를 생성해줘.
포함할 내용:
- 프로젝트 개요 및 주요 기능
- 기술 스택
- 설치 및 실행 방법
- API 엔드포인트 문서
- 추출 로직 설명 (규칙 기반 + LLM 기반)
- 프로젝트 구조
- 데이터베이스 스키마
- 테스트 실행 방법
```

Generated Code Snippets:
```
week2/README.md (lines 1-197)
- 프로젝트 개요: 자유 형식 노트에서 액션 아이템 자동 추출
- 기술 스택: FastAPI, SQLite, Vanilla JS, Google Gemini API
- 설정 및 실행: conda 환경, poetry 설치, .env 설정
- API 엔드포인트: Notes (POST/GET), Action Items (extract/extract-llm/done)
- 추출 로직: 규칙 기반 (패턴 매칭 + 명령형 문장 감지), LLM 기반
- 프로젝트 구조: app/, frontend/, tests/, data/
- 데이터베이스 스키마: notes, action_items 테이블
- 테스트 실행: pytest 명령어
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 