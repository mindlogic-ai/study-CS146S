# Expense Tracker (가계부) — Design Spec

## App Concept

개인 가계부 웹 앱. 수입/지출을 기록하고, 카테고리별·월별로 요약과 차트를 제공한다.
3개의 서로 다른 기술 스택으로 동일한 기능을 구현한다.

## Functional Requirements

### Core Features
- **거래 CRUD**: 수입/지출 생성, 조회, 수정, 삭제
- **고정 카테고리**: 지출(식비, 교통, 쇼핑, 주거, 여가, 기타), 수입(급여, 용돈, 기타수입)
- **요약**: 이번 달 총수입, 총지출, 잔액 표시
- **차트**: 카테고리별 파이차트, 월별 바차트
- **필터링**: 기간, 카테고리, 타입(수입/지출)별 필터

### Non-Goals
- 사용자 인증/로그인
- 사용자 정의 카테고리
- 다중 통화
- 배포 (로컬 실행만)

## Data Model

### Transaction
| Field       | Type              | Description              |
|-------------|-------------------|--------------------------|
| id          | Integer (PK, AI)  | 자동 증가 기본키           |
| type        | String            | `income` 또는 `expense`   |
| category    | String            | 고정 카테고리 중 하나       |
| amount      | Integer           | 금액 (원 단위, 정수)       |
| description | String (nullable) | 메모                      |
| date        | Date              | 거래 날짜                  |
| created_at  | DateTime          | 자동 생성 타임스탬프        |

### Fixed Categories
- **Expense**: 식비, 교통, 쇼핑, 주거, 여가, 기타
- **Income**: 급여, 용돈, 기타수입

## API Endpoints

| Method | Path                  | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | `/api/transactions`   | 목록 조회 (query: month, category, type) |
| POST   | `/api/transactions`   | 거래 생성 (201)                       |
| PATCH  | `/api/transactions/:id` | 거래 수정                            |
| DELETE | `/api/transactions/:id` | 거래 삭제                            |
| GET    | `/api/summary`        | 월별/카테고리별 요약 데이터             |

### Query Parameters (GET /api/transactions)
- `month`: YYYY-MM 형식 (기본값: 현재 월)
- `category`: 카테고리 필터
- `type`: income 또는 expense

### Summary Response (GET /api/summary)
```json
{
  "month": "2026-03",
  "total_income": 3000000,
  "total_expense": 1500000,
  "balance": 1500000,
  "by_category": [
    { "category": "식비", "total": 500000 },
    { "category": "교통", "total": 200000 }
  ]
}
```

## UI Design

단일 페이지 레이아웃:

1. **헤더**: 앱 제목
2. **요약 카드**: 총수입, 총지출, 잔액 (3개 카드)
3. **차트 영역**: 카테고리별 파이차트 + 월별 바차트
4. **거래 추가 버튼**: 클릭 시 모달 폼 표시
5. **필터 바**: 기간, 카테고리, 타입 필터
6. **거래 목록 테이블**: 날짜, 카테고리, 메모, 금액, 수정/삭제 버튼

### Style
- 미니멀 디자인, 별도 UI 프레임워크 없이 CSS
- 수입: 파란색, 지출: 빨간색
- 금액 표시: ₩ 원화 포맷

## Tech Stacks

### Version 1: Django + Vanilla JS + SQLite
- **Folder**: `week8/django-expense-tracker/`
- **Backend**: Django 5.x, Django ORM
- **Frontend**: Vanilla JS + HTML + CSS (Django 템플릿 또는 static files)
- **Chart**: Chart.js (CDN)
- **DB**: SQLite (Django 기본)

### Version 2: Express + React + SQLite
- **Folder**: `week8/express-react-expense-tracker/`
- **Backend**: Express.js, better-sqlite3
- **Frontend**: React (Vite)
- **Chart**: Recharts
- **DB**: SQLite (better-sqlite3)
- **구조**: API 서버 + SPA 클라이언트 분리

### Version 3: Next.js + Prisma + SQLite
- **Folder**: `week8/nextjs-expense-tracker/`
- **Backend**: Next.js API Routes
- **Frontend**: React (Next.js 내장)
- **Chart**: Recharts
- **DB**: SQLite (Prisma ORM)
- **구조**: 풀스택 단일 프로젝트

## Note on bolt.new
과제 원본은 bolt.new 사용을 요구하지만, 유료 플랜이 필요하여 대체하기로 결정.
3개 스택 모두 직접 구현한다.

## Deliverables

### 각 프로젝트 폴더 README.md
각 버전 폴더에 README.md 포함:
- Prerequisites (Python/Node 버전 등)
- 설치 방법 (`pip install` / `npm install`)
- 실행 방법
- 알려진 이슈 및 참고사항

### writeup.md
`week8/writeup.md`에 작성:
- App Concept (가계부 앱 설명)
- 3개 버전 각각의 App Description (스택, 구현 방식, 특이사항)

## Implementation Order
1. Django (Python 익숙, 가장 빠르게 완성)
2. Express + React (API/프론트 분리 구조)
3. Next.js + Prisma (React 재활용, SSR 풀스택)

## Seed Data
각 스택에 동일한 시드 데이터 포함:
- 최근 2개월 치 샘플 거래 10~15건
