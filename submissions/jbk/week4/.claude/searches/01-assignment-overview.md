# Week 4 과제 개요 조사

## 과제 목표
Claude Code 기능을 활용하여 **최소 2개의 자동화(automation)**를 구축하고, 이를 사용하여 스타터 앱을 개선한다.

## 선택 가능한 자동화 카테고리

### A) Custom Slash Commands (`.claude/commands/*.md`)
- 반복적인 워크플로우를 Markdown 파일로 정의
- `/` 명령어로 실행 가능
- 예시:
  - `tests.md`: pytest 실행 + coverage
  - `docs-sync.md`: OpenAPI → API.md 동기화
  - `refactor-module.md`: 모듈 이름 변경 + import 업데이트

### B) CLAUDE.md Guidance Files
- 세션 시작 시 자동으로 읽히는 지침 파일
- 예시:
  - 코드 네비게이션, 엔트리 포인트 문서화
  - 스타일 가이드, 안전 가드레일
  - 워크플로우 스니펫 (TDD 등)

### C) SubAgents (역할 특화 에이전트)
- 각각의 시스템 프롬프트, 도구, 컨텍스트를 가진 특화 AI 에이전트
- 예시:
  - TestAgent + CodeAgent (TDD 워크플로우)
  - DocsAgent + CodeAgent (문서 자동화)
  - DBAgent + RefactorAgent (스키마 변경)

## 제출물
1. 2개 이상의 자동화 (slash commands, CLAUDE.md, SubAgent 조합)
2. `writeup.md` 작성:
   - 디자인 영감 (best-practices/sub-agents 문서 인용)
   - 각 자동화의 목표, 입출력, 단계
   - 실행 방법 (정확한 명령어), 예상 출력, 안전 노트
   - Before vs. After 비교
   - 스타터 앱 개선에 어떻게 활용했는지

## 스타터 앱 개선 가능 작업 (docs/TASKS.md)
1. Pre-commit 설정 및 코드 정리
2. Notes 검색 엔드포인트 (case-insensitive)
3. Action item 완료 플로우
4. 추출 로직 개선 (#tag 파싱)
5. Notes CRUD 확장 (PUT, DELETE)
6. 요청 유효성 검사 및 에러 처리
7. API 문서 drift 체크
