# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **MJK** \
SUNet ID: **mjk** \
Citations: **Claude Code (AI assistant)**

This assignment took me about **3 hours** to do. 


## App Concept
```
개인 가계부(Expense Tracker) 웹 앱. 수입과 지출을 기록하고, 카테고리별·월별 요약 및 차트 시각화를 제공한다. 주요 기능: 거래(수입/지출) CRUD, 고정 카테고리 분류, 월별 총수입·총지출·잔액 요약, 카테고리별 파이차트 및 수입/지출 바차트, 기간·카테고리·타입별 필터링.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: django-expense-tracker
AI app generation platform: Claude Code
Tech Stack: Django 5.x + Vanilla JavaScript + SQLite
Persistence: SQLite (Django ORM)
Frameworks/Libraries Used: Django 5.x, Chart.js (CDN)

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: Django CSRF 토큰 이슈 — csrf_exempt 데코레이터로 해결. 정적 파일 서빙 설정이 필요했음.

b. Prompting: 모델과 뷰를 단계적으로 나눠서 구현 지시하니 잘 작동함. 한 번에 전체를 만들라고 하면 누락이 생길 수 있음.

c. Approximate time-to-first-run and time-to-feature metrics: 첫 실행까지 약 15분, 전체 기능 구현까지 약 40분
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: express-react-expense-tracker
AI app generation platform: Claude Code
Tech Stack: Express.js + React (Vite) + SQLite
Persistence: SQLite (better-sqlite3)
Frameworks/Libraries Used: Express.js, React 18, Vite, Recharts, better-sqlite3, cors

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: CORS 설정 필요 (서버 3001, 클라이언트 5173 포트 분리). Vite proxy 설정으로 개발 환경에서 해결.

b. Prompting: 서버와 클라이언트를 분리해서 지시하니 깔끔하게 구현됨. 컴포넌트를 개별적으로 지시하는 것이 효과적이었음.

c. Approximate time-to-first-run and time-to-feature metrics: 첫 실행까지 약 20분, 전체 기능 구현까지 약 50분
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: nextjs-expense-tracker
AI app generation platform: Claude Code
Tech Stack: Next.js 14 (App Router) + Prisma + SQLite
Persistence: SQLite (Prisma ORM)
Frameworks/Libraries Used: Next.js 14, React 18, Prisma 5, Recharts

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: Prisma 초기 설정(generate, db push)이 필요. Next.js App Router의 API 라우트 구조 적응 필요.

b. Prompting: Prisma 스키마를 먼저 정의하고 API 라우트를 만든 후 프론트엔드를 구현하는 순서가 효과적이었음. Express+React에서 만든 컴포넌트를 재활용할 수 있어 빠르게 진행됨.

c. Approximate time-to-first-run and time-to-feature metrics: 첫 실행까지 약 15분, 전체 기능 구현까지 약 40분
```
