# Claude Code Best Practices 조사

> 출처: https://code.claude.com/docs/en/best-practices

## 핵심 원칙: 컨텍스트 윈도우 관리가 가장 중요
- Claude의 컨텍스트 윈도우는 대화, 파일 읽기, 명령 출력 등으로 빠르게 채워짐
- 채워질수록 성능 저하 → 적극적 관리 필요
- `/clear`로 무관한 작업 간 리셋, `/compact`로 압축

## 1. 검증 수단 제공 (가장 중요한 단일 팁)
- 테스트, 스크린샷, 예상 출력 제공하여 Claude가 스스로 검증 가능하게
- Before: "이메일 유효성 함수 구현해줘"
- After: "validateEmail 함수 작성해. user@example.com은 true, invalid는 false. 구현 후 테스트 실행해"

## 2. 탐색 → 계획 → 코드 (4단계 워크플로우)
1. **Explore**: Plan Mode에서 파일 읽기/질문
2. **Plan**: 상세 구현 계획 작성
3. **Implement**: Normal Mode로 코딩, 계획 대비 검증
4. **Commit**: 커밋 + PR 생성

## 3. 구체적 컨텍스트 제공
- 파일명, 제약 조건, 패턴 참조 명시
- `@`로 파일 참조, 이미지 붙여넣기, URL 제공
- Before: "foo.py 테스트 추가해"
- After: "foo.py에 로그아웃 엣지케이스 테스트 작성. mock 사용 금지"

## 4. 효과적인 CLAUDE.md 작성
- `/init`으로 기본 생성 후 개선
- **포함할 것**: Claude가 추론할 수 없는 bash 명령, 기본과 다른 스타일 규칙, 테스트 지침, 아키텍처 결정
- **제외할 것**: 코드에서 파악 가능한 것, 표준 언어 규칙, 자주 변하는 정보, 긴 설명
- 과도하면 Claude가 무시 → 간결하게 유지
- "IMPORTANT", "YOU MUST" 등으로 강조 가능

## 5. SubAgent 활용 패턴
- 리서치/탐색을 서브에이전트에 위임 → 메인 컨텍스트 보존
- 구현 후 코드 리뷰도 서브에이전트로 분리 가능
- Writer/Reviewer 패턴: 세션 A가 구현, 세션 B가 리뷰

## 6. 일반적 실패 패턴 회피
- **Kitchen sink session**: 무관한 작업 혼합 → `/clear` 사용
- **반복 수정**: 2번 실패 후 `/clear` + 더 나은 프롬프트로 재시작
- **과대한 CLAUDE.md**: 규칙이 노이즈에 묻힘 → 과감히 정리
- **검증 없는 신뢰**: 항상 테스트/검증 수단 제공
- **무한 탐색**: 범위 지정 안 한 조사 → 서브에이전트 사용

## TDD에 특히 관련된 Best Practices
1. 테스트를 검증 수단으로 제공하면 Claude 성능이 극적으로 향상
2. "실패하는 테스트 먼저 작성 → 구현 → 검증" 패턴이 가장 효과적
3. Writer/Reviewer 패턴 = TestAgent/CodeAgent 패턴과 동일
4. 서브에이전트로 테스트 실행하면 메인 컨텍스트 오염 방지
