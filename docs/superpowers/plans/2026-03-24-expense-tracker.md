# Expense Tracker (가계부) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the same expense tracker app in 3 stacks (Django, Express+React, Next.js+Prisma) for the CS146S Week 8 assignment.

**Architecture:** Each stack implements identical CRUD for transactions with fixed categories, a summary endpoint for aggregation, and a single-page UI with charts. All use SQLite for persistence.

**Tech Stack:** Django 5.x + Vanilla JS | Express + React (Vite) + better-sqlite3 | Next.js + Prisma + SQLite

**Spec:** `docs/superpowers/specs/2026-03-24-expense-tracker-design.md`

---

## Shared Constants

These values are identical across all 3 stacks:

```
EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"]
INCOME_CATEGORIES = ["급여", "용돈", "기타수입"]
TRANSACTION_TYPES = ["income", "expense"]
```

Seed data (same across all stacks):
```json
[
  {"type":"expense","category":"식비","amount":15000,"description":"점심 김치찌개","date":"2026-03-01"},
  {"type":"expense","category":"교통","amount":3000,"description":"버스비","date":"2026-03-02"},
  {"type":"expense","category":"쇼핑","amount":45000,"description":"운동화","date":"2026-03-05"},
  {"type":"income","category":"급여","amount":3500000,"description":"3월 급여","date":"2026-03-10"},
  {"type":"expense","category":"여가","amount":12000,"description":"영화 관람","date":"2026-03-12"},
  {"type":"expense","category":"주거","amount":500000,"description":"월세","date":"2026-03-15"},
  {"type":"expense","category":"식비","amount":8000,"description":"저녁 국밥","date":"2026-03-18"},
  {"type":"income","category":"용돈","amount":100000,"description":"부모님 용돈","date":"2026-03-20"},
  {"type":"expense","category":"교통","amount":55000,"description":"교통카드 충전","date":"2026-02-05"},
  {"type":"expense","category":"식비","amount":25000,"description":"회식","date":"2026-02-10"},
  {"type":"income","category":"급여","amount":3500000,"description":"2월 급여","date":"2026-02-10"},
  {"type":"expense","category":"쇼핑","amount":32000,"description":"책 구매","date":"2026-02-15"},
  {"type":"expense","category":"여가","amount":20000,"description":"카페","date":"2026-02-20"}
]
```

---

## Task 1: Django — Project Setup & Model

**Files:**
- Create: `week8/django-expense-tracker/requirements.txt`
- Create: `week8/django-expense-tracker/manage.py`
- Create: `week8/django-expense-tracker/config/__init__.py`
- Create: `week8/django-expense-tracker/config/settings.py`
- Create: `week8/django-expense-tracker/config/urls.py`
- Create: `week8/django-expense-tracker/tracker/__init__.py`
- Create: `week8/django-expense-tracker/tracker/models.py`

- [ ] **Step 1: Create requirements.txt**

```
django>=5.0
```

- [ ] **Step 2: Create Django project structure**

Create `manage.py`, `config/settings.py`, `config/urls.py`, `config/__init__.py` using standard Django scaffolding. In `settings.py`, configure:
- `INSTALLED_APPS` includes `tracker`
- `DATABASES` uses SQLite at `db.sqlite3`
- `STATIC_URL = "/static/"` and `STATICFILES_DIRS` pointing to a `static/` folder

- [ ] **Step 3: Create Transaction model**

```python
# tracker/models.py
from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPES = [("income", "Income"), ("expense", "Expense")]

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=200, blank=True, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
```

- [ ] **Step 4: Run migrations**

```bash
cd week8/django-expense-tracker
pip install -r requirements.txt
python manage.py makemigrations tracker
python manage.py migrate
```

- [ ] **Step 5: Commit**

```bash
git add week8/django-expense-tracker/
git commit -m "feat(django): project setup and Transaction model"
```

---

## Task 2: Django — API Views

**Files:**
- Create: `week8/django-expense-tracker/tracker/views.py`
- Modify: `week8/django-expense-tracker/config/urls.py`

- [ ] **Step 1: Create API views**

```python
# tracker/views.py
import json
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from .models import Transaction

EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"]
INCOME_CATEGORIES = ["급여", "용돈", "기타수입"]

@csrf_exempt
def transactions(request):
    if request.method == "GET":
        qs = Transaction.objects.all()
        month = request.GET.get("month")  # YYYY-MM
        category = request.GET.get("category")
        tx_type = request.GET.get("type")
        if month:
            year, m = month.split("-")
            qs = qs.filter(date__year=int(year), date__month=int(m))
        if category:
            qs = qs.filter(category=category)
        if tx_type:
            qs = qs.filter(type=tx_type)
        data = list(qs.values("id", "type", "category", "amount", "description", "date", "created_at"))
        for d in data:
            d["date"] = d["date"].isoformat()
            d["created_at"] = d["created_at"].isoformat()
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        body = json.loads(request.body)
        tx = Transaction.objects.create(
            type=body["type"],
            category=body["category"],
            amount=body["amount"],
            description=body.get("description", ""),
            date=body["date"],
        )
        return JsonResponse({"id": tx.id}, status=201)

@csrf_exempt
def transaction_detail(request, pk):
    try:
        tx = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "PATCH":
        body = json.loads(request.body)
        for field in ["type", "category", "amount", "description", "date"]:
            if field in body:
                setattr(tx, field, body[field])
        tx.save()
        return JsonResponse({"id": tx.id})

    if request.method == "DELETE":
        tx.delete()
        return JsonResponse({"ok": True})

def summary(request):
    month = request.GET.get("month")
    if not month:
        today = date.today()
        month = today.strftime("%Y-%m")
    year, m = month.split("-")
    qs = Transaction.objects.filter(date__year=int(year), date__month=int(m))

    total_income = qs.filter(type="income").aggregate(s=Sum("amount"))["s"] or 0
    total_expense = qs.filter(type="expense").aggregate(s=Sum("amount"))["s"] or 0
    by_category = list(
        qs.values("category").annotate(total=Sum("amount")).order_by("-total")
    )
    return JsonResponse({
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "by_category": by_category,
    })

def categories(request):
    return JsonResponse({
        "expense": EXPENSE_CATEGORIES,
        "income": INCOME_CATEGORIES,
    })
```

- [ ] **Step 2: Wire URLs**

```python
# config/urls.py
from django.urls import path
from tracker import views

urlpatterns = [
    path("api/transactions", views.transactions),
    path("api/transactions/<int:pk>", views.transaction_detail),
    path("api/summary", views.summary),
    path("api/categories", views.categories),
]
```

- [ ] **Step 3: Test endpoints manually**

```bash
cd week8/django-expense-tracker
python manage.py runserver
# In another terminal:
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","category":"식비","amount":15000,"description":"테스트","date":"2026-03-24"}'
curl http://localhost:8000/api/transactions
curl http://localhost:8000/api/summary
```

- [ ] **Step 4: Commit**

```bash
git add week8/django-expense-tracker/
git commit -m "feat(django): API views for transactions and summary"
```

---

## Task 3: Django — Frontend (Vanilla JS)

**Files:**
- Create: `week8/django-expense-tracker/static/index.html`
- Create: `week8/django-expense-tracker/static/app.js`
- Create: `week8/django-expense-tracker/static/styles.css`
- Modify: `week8/django-expense-tracker/config/urls.py` (add static serving)
- Modify: `week8/django-expense-tracker/config/settings.py` (add STATICFILES_DIRS)

- [ ] **Step 1: Configure static file serving**

Add to `config/urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns += [
    path("", RedirectView.as_view(url="/static/index.html")),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
```

- [ ] **Step 2: Create index.html**

Single-page HTML with:
- Summary cards (총수입, 총지출, 잔액)
- Chart containers (2 canvas elements for Chart.js)
- Filter bar (month picker, category dropdown, type dropdown)
- Add transaction button
- Transaction table
- Modal form for add/edit
- Chart.js CDN script tag

- [ ] **Step 3: Create styles.css**

Minimal CSS:
- Card layout (flexbox)
- Table styling
- Modal styling
- Color coding: income (blue `#2196F3`), expense (red `#f44336`)
- Responsive layout

- [ ] **Step 4: Create app.js**

Vanilla JS implementing:
- `fetchTransactions()` — GET /api/transactions with filters, render table
- `fetchSummary()` — GET /api/summary, update cards
- `renderCharts()` — Chart.js pie chart (by category) + bar chart (monthly)
- `showModal()` / `hideModal()` — form for add/edit
- `saveTransaction()` — POST or PATCH
- `deleteTransaction(id)` — DELETE with confirm
- `formatCurrency(amount)` — ₩ 원화 포맷
- Event listeners for filters, buttons

- [ ] **Step 5: Verify in browser**

```bash
python manage.py runserver
# Open http://localhost:8000
```

Verify: CRUD works, charts render, filters work, summary cards update.

- [ ] **Step 6: Commit**

```bash
git add week8/django-expense-tracker/
git commit -m "feat(django): frontend with Vanilla JS and Chart.js"
```

---

## Task 4: Django — Seed Data & README

**Files:**
- Create: `week8/django-expense-tracker/tracker/management/commands/seed.py`
- Create: `week8/django-expense-tracker/README.md`

- [ ] **Step 1: Create seed management command**

```python
# tracker/management/commands/seed.py
from django.core.management.base import BaseCommand
from tracker.models import Transaction

SEED_DATA = [
    # ... (use shared seed data from top of plan)
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        Transaction.objects.all().delete()
        for item in SEED_DATA:
            Transaction.objects.create(**item)
        self.stdout.write(f"Seeded {len(SEED_DATA)} transactions")
```

Create `tracker/management/__init__.py` and `tracker/management/commands/__init__.py`.

- [ ] **Step 2: Run seed**

```bash
python manage.py seed
```

- [ ] **Step 3: Create README.md**

Include: prerequisites (Python 3.10+), install (`pip install -r requirements.txt`), setup (`python manage.py migrate && python manage.py seed`), run (`python manage.py runserver`), access URL.

- [ ] **Step 4: Commit**

```bash
git add week8/django-expense-tracker/
git commit -m "feat(django): seed data and README"
```

---

## Task 5: Express + React — Backend Setup

**Files:**
- Create: `week8/express-react-expense-tracker/server/package.json`
- Create: `week8/express-react-expense-tracker/server/index.js`
- Create: `week8/express-react-expense-tracker/server/db.js`
- Create: `week8/express-react-expense-tracker/server/seed.js`

- [ ] **Step 1: Create server/package.json**

```json
{
  "name": "expense-tracker-server",
  "type": "module",
  "scripts": {
    "start": "node index.js",
    "seed": "node seed.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "better-sqlite3": "^11.0.0",
    "cors": "^2.8.0"
  }
}
```

- [ ] **Step 2: Create db.js**

```javascript
// server/db.js
import Database from "better-sqlite3";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const db = new Database(join(__dirname, "data.db"));

db.exec(`
  CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  )
`);

export default db;
```

- [ ] **Step 3: Create index.js with all routes**

Express server on port 3001 with:
- `GET /api/transactions` — query filters: month, category, type
- `POST /api/transactions` — create (201)
- `PATCH /api/transactions/:id` — partial update
- `DELETE /api/transactions/:id` — delete
- `GET /api/summary` — aggregate by month
- `GET /api/categories` — return fixed categories
- CORS enabled for localhost:5173 (Vite dev)

- [ ] **Step 4: Create seed.js**

Insert shared seed data into SQLite.

- [ ] **Step 5: Install, seed, and test**

```bash
cd week8/express-react-expense-tracker/server
npm install
npm run seed
npm start
# Test with curl
curl http://localhost:3001/api/transactions
curl http://localhost:3001/api/summary
```

- [ ] **Step 6: Commit**

```bash
git add week8/express-react-expense-tracker/server/
git commit -m "feat(express): backend API with SQLite"
```

---

## Task 6: Express + React — Frontend

**Files:**
- Create: `week8/express-react-expense-tracker/client/package.json`
- Create: `week8/express-react-expense-tracker/client/vite.config.js`
- Create: `week8/express-react-expense-tracker/client/index.html`
- Create: `week8/express-react-expense-tracker/client/src/main.jsx`
- Create: `week8/express-react-expense-tracker/client/src/App.jsx`
- Create: `week8/express-react-expense-tracker/client/src/App.css`
- Create: `week8/express-react-expense-tracker/client/src/components/SummaryCards.jsx`
- Create: `week8/express-react-expense-tracker/client/src/components/Charts.jsx`
- Create: `week8/express-react-expense-tracker/client/src/components/TransactionTable.jsx`
- Create: `week8/express-react-expense-tracker/client/src/components/TransactionForm.jsx`
- Create: `week8/express-react-expense-tracker/client/src/components/Filters.jsx`

- [ ] **Step 1: Scaffold React client with Vite**

`package.json` with dependencies: react, react-dom, recharts.
`vite.config.js` with proxy to `http://localhost:3001/api`.

- [ ] **Step 2: Create App.jsx**

Main component managing state:
- `transactions`, `summary`, `filters` (month, category, type)
- `editingTransaction` (null or transaction object for modal)
- Fetch on mount and filter change
- Pass props to child components

- [ ] **Step 3: Create SummaryCards component**

Three cards: 총수입 (blue), 총지출 (red), 잔액 (green/red based on sign).
Format amounts with `₩` and `toLocaleString()`.

- [ ] **Step 4: Create Charts component**

Using Recharts:
- `PieChart` for category breakdown
- `BarChart` placeholder for monthly (or use summary data)

- [ ] **Step 5: Create TransactionTable component**

Table with columns: 날짜, 타입, 카테고리, 메모, 금액, 액션(수정/삭제).
Color code amounts. Delete with `window.confirm`.

- [ ] **Step 6: Create TransactionForm component**

Modal form with fields: type (radio), category (select — changes based on type), amount, date, description.
Used for both create and edit.

- [ ] **Step 7: Create Filters component**

Month input (`type="month"`), category select, type select.

- [ ] **Step 8: Create App.css**

Same styling approach as Django version.

- [ ] **Step 9: Verify in browser**

```bash
cd week8/express-react-expense-tracker/client
npm install
npm run dev
# Open http://localhost:5173
# (server must be running on :3001)
```

- [ ] **Step 10: Commit**

```bash
git add week8/express-react-expense-tracker/client/
git commit -m "feat(express-react): React frontend with Recharts"
```

---

## Task 7: Express + React — README

**Files:**
- Create: `week8/express-react-expense-tracker/README.md`

- [ ] **Step 1: Create README.md**

Include:
- Prerequisites (Node.js 18+)
- Install: `cd server && npm install` + `cd client && npm install`
- Seed: `cd server && npm run seed`
- Run: `cd server && npm start` (terminal 1) + `cd client && npm run dev` (terminal 2)
- Access URL

- [ ] **Step 2: Commit**

```bash
git add week8/express-react-expense-tracker/README.md
git commit -m "feat(express-react): README"
```

---

## Task 8: Next.js + Prisma — Setup & Schema

**Files:**
- Create: `week8/nextjs-expense-tracker/package.json`
- Create: `week8/nextjs-expense-tracker/prisma/schema.prisma`
- Create: `week8/nextjs-expense-tracker/prisma/seed.js`
- Create: `week8/nextjs-expense-tracker/src/lib/prisma.js`
- Create: `week8/nextjs-expense-tracker/next.config.js`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "nextjs-expense-tracker",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "seed": "node prisma/seed.js"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@prisma/client": "^5.0.0",
    "recharts": "^2.0.0"
  },
  "devDependencies": {
    "prisma": "^5.0.0"
  },
  "prisma": {
    "seed": "node prisma/seed.js"
  }
}
```

- [ ] **Step 2: Create Prisma schema**

```prisma
// prisma/schema.prisma
datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}

generator client {
  provider = "prisma-client-js"
}

model Transaction {
  id          Int      @id @default(autoincrement())
  type        String   // "income" or "expense"
  category    String
  amount      Int
  description String   @default("")
  date        DateTime
  createdAt   DateTime @default(now())
}
```

- [ ] **Step 3: Create prisma client singleton**

```javascript
// src/lib/prisma.js
import { PrismaClient } from "@prisma/client";
const globalForPrisma = globalThis;
const prisma = globalForPrisma.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
export default prisma;
```

- [ ] **Step 4: Create seed.js**

Use `@prisma/client` to insert shared seed data.

- [ ] **Step 5: Initialize**

```bash
cd week8/nextjs-expense-tracker
npm install
npx prisma generate
npx prisma db push
npm run seed
```

- [ ] **Step 6: Commit**

```bash
git add week8/nextjs-expense-tracker/
git commit -m "feat(nextjs): project setup with Prisma schema"
```

---

## Task 9: Next.js — API Routes

**Files:**
- Create: `week8/nextjs-expense-tracker/src/app/api/transactions/route.js`
- Create: `week8/nextjs-expense-tracker/src/app/api/transactions/[id]/route.js`
- Create: `week8/nextjs-expense-tracker/src/app/api/summary/route.js`
- Create: `week8/nextjs-expense-tracker/src/app/api/categories/route.js`

- [ ] **Step 1: Create transactions route (GET, POST)**

```javascript
// src/app/api/transactions/route.js
import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const month = searchParams.get("month");
  const category = searchParams.get("category");
  const type = searchParams.get("type");

  const where = {};
  if (month) {
    const [year, m] = month.split("-");
    const start = new Date(year, m - 1, 1);
    const end = new Date(year, m, 1);
    where.date = { gte: start, lt: end };
  }
  if (category) where.category = category;
  if (type) where.type = type;

  const transactions = await prisma.transaction.findMany({
    where,
    orderBy: [{ date: "desc" }, { createdAt: "desc" }],
  });
  return NextResponse.json(transactions);
}

export async function POST(request) {
  const body = await request.json();
  const tx = await prisma.transaction.create({
    data: {
      type: body.type,
      category: body.category,
      amount: body.amount,
      description: body.description || "",
      date: new Date(body.date),
    },
  });
  return NextResponse.json({ id: tx.id }, { status: 201 });
}
```

- [ ] **Step 2: Create transaction detail route (PATCH, DELETE)**

`src/app/api/transactions/[id]/route.js` with PATCH and DELETE handlers.

- [ ] **Step 3: Create summary route**

`src/app/api/summary/route.js` — aggregate using Prisma `groupBy` or raw query.

- [ ] **Step 4: Create categories route**

Return fixed categories JSON.

- [ ] **Step 5: Test API**

```bash
cd week8/nextjs-expense-tracker
npm run dev
curl http://localhost:3000/api/transactions
curl http://localhost:3000/api/summary
```

- [ ] **Step 6: Commit**

```bash
git add week8/nextjs-expense-tracker/src/app/api/
git commit -m "feat(nextjs): API routes for transactions and summary"
```

---

## Task 10: Next.js — Frontend Pages & Components

**Files:**
- Create: `week8/nextjs-expense-tracker/src/app/layout.js`
- Create: `week8/nextjs-expense-tracker/src/app/page.js`
- Create: `week8/nextjs-expense-tracker/src/app/globals.css`
- Create: `week8/nextjs-expense-tracker/src/components/SummaryCards.jsx`
- Create: `week8/nextjs-expense-tracker/src/components/Charts.jsx`
- Create: `week8/nextjs-expense-tracker/src/components/TransactionTable.jsx`
- Create: `week8/nextjs-expense-tracker/src/components/TransactionForm.jsx`
- Create: `week8/nextjs-expense-tracker/src/components/Filters.jsx`

- [ ] **Step 1: Create layout.js and globals.css**

Basic Next.js layout with global styles (same approach as other stacks).

- [ ] **Step 2: Create page.js (main page)**

`"use client"` directive. Same state management pattern as Express+React App.jsx.
Fetch from `/api/transactions` and `/api/summary`.

- [ ] **Step 3: Create components**

Reuse same component logic from Express+React version:
- SummaryCards, Charts (Recharts), TransactionTable, TransactionForm, Filters
- Adapt imports (no proxy needed — same-origin API)

- [ ] **Step 4: Verify in browser**

```bash
npm run dev
# Open http://localhost:3000
```

- [ ] **Step 5: Commit**

```bash
git add week8/nextjs-expense-tracker/src/
git commit -m "feat(nextjs): frontend pages and components"
```

---

## Task 11: Next.js — README

**Files:**
- Create: `week8/nextjs-expense-tracker/README.md`

- [ ] **Step 1: Create README.md**

Include: prerequisites (Node.js 18+), install (`npm install`), setup (`npx prisma db push && npm run seed`), run (`npm run dev`), access URL.

- [ ] **Step 2: Commit**

```bash
git add week8/nextjs-expense-tracker/README.md
git commit -m "feat(nextjs): README"
```

---

## Task 12: writeup.md

**Files:**
- Modify: `week8/writeup.md`

- [ ] **Step 1: Fill out writeup.md**

Fill in all TODO sections:
- Submission details
- App Concept: 개인 가계부 앱 — 수입/지출 CRUD, 카테고리별·월별 요약, 차트 시각화
- Version 1: Django + Vanilla JS + SQLite (django-expense-tracker/)
- Version 2: Express + React + SQLite (express-react-expense-tracker/)
- Version 3: Next.js + Prisma + SQLite (nextjs-expense-tracker/)
- Each version: folder name, stack, persistence, frameworks, reflections

- [ ] **Step 2: Commit**

```bash
git add week8/writeup.md
git commit -m "docs: complete writeup.md for week8"
```
