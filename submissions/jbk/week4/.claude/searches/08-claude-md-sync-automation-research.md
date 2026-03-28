# CLAUDE.md Sync 자동화 조사

## 개요
과제에서 선택할 자동화 #2: **CLAUDE.md 동기화 자동화**
- 코드 변경 시 CLAUDE.md가 자동으로 실제 코드 상태를 반영하도록 동기화
- 과제 assignment.md의 "B) CLAUDE.md guidance files" + "A) Slash commands - docs-sync" 결합

## 핵심 아이디어
1. `/sync-claude-md` 슬래시 커맨드로 CLAUDE.md 동기화 트리거
2. 실제 코드 구조를 분석하여 CLAUDE.md 자동 생성/업데이트
3. API 엔드포인트, 모델, 테스트 상태 등을 반영

## Best Practices 기반 설계 원칙

### Claude Code Best Practices에서
1. **"CLAUDE.md는 Claude가 추론할 수 없는 것만 포함"** → 코드에서 추출 가능한 구조 정보는 자동화
2. **"간결하고 액션 가능하게"** → 자동 생성 시에도 이 원칙 유지
3. **"프롬프트처럼 반복 개선"** → 동기화 도구로 반복 개선 자동화
4. **"과대한 CLAUDE.md 방지"** → 필요한 정보만 선별적으로 포함

### Docs Sync 패턴에서 (assignment.md)
1. OpenAPI spec 읽기 → API 문서 업데이트
2. 변경 사항 diff-like 요약
3. TODO 목록 생성

## 동기화할 정보

### 1. API 엔드포인트 목록 (자동 추출)
- `/openapi.json`에서 현재 엔드포인트 목록 가져오기
- 각 엔드포인트의 메서드, 경로, 응답 모델

### 2. 프로젝트 구조 (자동 추출)
- backend/app/ 하위 파일들과 역할
- 모델, 스키마, 라우터, 서비스 매핑

### 3. 개발 명령어 (고정)
- make run, make test, make format, make lint, make seed

### 4. 코드 스타일 규칙 (pyproject.toml에서 추출)
- black, ruff 설정
- line-length, 활성 규칙

### 5. 테스트 커버리지 상태 (자동 추출)
- 현재 테스트 파일 목록
- 어떤 기능이 테스트되어 있는지

## 구현 계획

### 슬래시 커맨드 (`.claude/commands/sync-claude-md.md`)
```yaml
---
name: sync-claude-md
description: Synchronize CLAUDE.md with current codebase state
disable-model-invocation: true
---

Synchronize the CLAUDE.md file with the current state of the codebase.

## Step 1: Analyze Current Codebase
- Read all Python files in backend/app/ to understand current structure
- Check backend/app/routers/ for current API endpoints
- Check backend/app/models.py for current database models
- Check backend/app/schemas.py for current Pydantic schemas
- Check backend/app/services/ for current services
- Check backend/tests/ for current test coverage
- Read pyproject.toml for code style configuration

## Step 2: Check API State
- Start the app briefly or read router files to list all endpoints
- Document each endpoint: method, path, request/response schemas
- Note any endpoints missing tests

## Step 3: Generate Updated CLAUDE.md
Update the CLAUDE.md file with the following sections:

### Project Overview
- App name, description, tech stack

### Quick Commands
- make run, test, format, lint, seed

### Architecture
- Entry point, routers, models, schemas, services, tests, frontend

### API Endpoints (auto-synced)
- List all current endpoints with methods and schemas

### Code Style
- From pyproject.toml: black, ruff settings

### Testing Status
- Which features have tests
- Which features need tests

### Development Workflow
- How to add new endpoints (TDD flow)
- How to modify models
- How to run and verify changes

## Step 4: Report Changes
- Show what was added/removed/changed in CLAUDE.md
- List any issues found (e.g., endpoints without tests)
```

## 스타터 앱에 적용
1. 초기 CLAUDE.md 생성 (현재 비어있음)
2. TDD 자동화로 Notes CRUD 추가 후 `/sync-claude-md` 실행
3. 새로운 엔드포인트, 테스트 상태가 자동 반영되는지 확인

## Before vs After 비교
### Before (수동 워크플로우)
1. 코드 변경할 때마다 CLAUDE.md 수동 업데이트 필요
2. 어떤 정보를 넣어야 하는지 매번 고민
3. 실제 코드와 문서가 drift (불일치) 발생
4. 새 팀원이 Claude 사용 시 부정확한 가이드 제공
→ 문서 관리 부담, 신뢰성 저하

### After (자동화 워크플로우)
1. `/sync-claude-md` 한 번으로 전체 동기화
2. 실제 코드 상태를 분석하여 자동 생성
3. 항상 최신 상태의 CLAUDE.md 유지
4. 변경 사항 리포트로 drift 감지
→ 일관성 있고 신뢰할 수 있는 가이드
