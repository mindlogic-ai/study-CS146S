# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Min Jae Kim** \
Citations: **Claude Code (Anthropic AI assistant) — used for code generation, scaffolding, and iterative debugging across all three stacks**

This assignment took me about **3 hours** to do.


## App Concept
```
Expense Tracker (가계부) — A personal finance management web application that helps users track
their income and expenses with visual insights.

Core Features:
- Full CRUD operations for financial transactions (income & expense)
- Fixed category classification (Expense: 식비, 교통, 쇼핑, 주거, 여가, 기타 / Income: 급여, 용돈, 기타수입)
- Monthly summary dashboard showing total income, total expenses, and net balance
- Interactive data visualization: category-breakdown pie chart and income-vs-expense bar chart
- Filtering by date range, category, and transaction type (income/expense)
- Persistent storage with SQLite across all three versions
- Responsive single-page UI with modal-based transaction forms

The same functional application was implemented across three distinct technology stacks to compare
developer experience, architecture patterns, and ecosystem differences.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: django-expense-tracker
AI app generation platform: Claude Code (Anthropic)
Tech Stack: Python (Django 5.x) + Vanilla JavaScript + SQLite
Persistence: SQLite via Django ORM (auto-managed migrations)
Frameworks/Libraries Used:
  - Backend: Django 5.x (models, views, URL routing, management commands)
  - Frontend: Vanilla JavaScript (ES6+), Chart.js 4.x (CDN) for data visualization
  - Database: SQLite3 (Django's default, zero-config)

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - CSRF Protection: Django's built-in CSRF middleware blocked API POST/PATCH/DELETE requests
     from the frontend. Resolved by applying @csrf_exempt decorator to API views, which is
     acceptable for this assignment since there's no authentication.
   - Static File Serving: Needed to configure STATICFILES_DIRS and add a root URL redirect to
     /static/index.html. Django's development server handles static files automatically with
     DEBUG=True, but the URL routing required explicit setup.
   - Date Serialization: Django's DateField and DateTimeField objects aren't JSON-serializable
     by default. Resolved by manually calling .isoformat() on date fields before returning
     JsonResponse.

b. Prompting (what required additional guidance; what worked poorly/well):
   - Effective strategy: Breaking the implementation into layers — model first, then views/URLs,
     then frontend. This incremental approach let me verify each layer before building on top.
   - What worked well: Providing the exact data model schema upfront (field names, types,
     constraints) produced accurate ORM models on the first try.
   - What required guidance: The static file serving configuration needed specific instructions
     about STATICFILES_DIRS and the RedirectView for the root URL. Generic "serve static files"
     prompts led to incomplete configurations.
   - Vanilla JS was straightforward to generate since there's no build step or framework
     abstractions to get wrong.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run (server starts, page loads): ~10 minutes
   - Time to full CRUD functionality: ~25 minutes
   - Time to charts and filtering: ~40 minutes total
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: express-react-expense-tracker
AI app generation platform: Claude Code (Anthropic)
Tech Stack: Node.js (Express.js 4.x) + React 18 (Vite 5.x) + SQLite
Persistence: SQLite via better-sqlite3 (synchronous, no ORM — raw SQL with prepared statements)
Frameworks/Libraries Used:
  - Backend: Express.js 4.x, better-sqlite3, cors middleware
  - Frontend: React 18, Vite 5.x (dev server + HMR), Recharts 2.x (data visualization)
  - Build: @vitejs/plugin-react for JSX transformation

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - CORS Configuration: With the server on port 3001 and Vite dev server on port 5173,
     cross-origin requests were blocked. Resolved with two approaches: cors middleware on
     Express (for direct requests) and Vite's proxy configuration (proxying /api/* to
     localhost:3001 during development).
   - ES Module vs CommonJS: Using "type": "module" in package.json required adjusting import
     syntax and using fileURLToPath for __dirname equivalent. This is the modern Node.js
     approach but required attention to import semantics.
   - better-sqlite3 Native Module: This package requires native compilation (node-gyp).
     Worked out of the box on macOS with Xcode CLT installed, but worth noting for
     cross-platform compatibility.
   - SQL Date Filtering: SQLite stores dates as TEXT, so month-based filtering required
     string comparison (date >= '2026-03-01' AND date < '2026-04-01') rather than date
     functions. Careful string formatting was needed for month boundaries.

b. Prompting (what required additional guidance; what worked poorly/well):
   - Effective strategy: Implementing server and client as completely separate projects.
     Specifying the API contract first, then building each side independently.
   - What worked well: Component-by-component instructions for React (SummaryCards, Charts,
     TransactionTable, TransactionForm, Filters) produced clean, focused components with
     clear prop interfaces.
   - What required guidance: The Vite proxy configuration needed explicit specification —
     without it, the generated code tried to hardcode localhost:3001 URLs in the frontend.
   - Recharts integration was smooth; specifying the chart types (PieChart, BarChart) and
     data shape upfront produced working visualizations.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run (both servers start, page loads): ~15 minutes
   - Time to full CRUD functionality: ~35 minutes
   - Time to charts and filtering: ~50 minutes total
   - Note: Two-terminal setup (server + client) adds operational complexity vs Django's
     single-server approach
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: nextjs-expense-tracker
AI app generation platform: Claude Code (Anthropic)
Tech Stack: Next.js 14 (App Router) + Prisma 5 + SQLite
Persistence: SQLite via Prisma ORM (schema-first, type-safe database access)
Frameworks/Libraries Used:
  - Framework: Next.js 14 (App Router for both API routes and React pages)
  - ORM: Prisma 5 (schema definition, client generation, migrations)
  - Frontend: React 18 (built into Next.js), Recharts 2.x (data visualization)
  - Runtime: Node.js 18+

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Prisma Setup Ceremony: Unlike Django's manage.py migrate or raw SQL, Prisma requires a
     multi-step initialization: schema definition → prisma generate (client codegen) →
     prisma db push (apply schema) → seed. This is more steps but provides type-safe
     database access in return.
   - App Router API Conventions: Next.js 14's App Router uses file-system routing with
     specific export names (GET, POST, PATCH, DELETE functions). The [id] dynamic segment
     syntax and async params handling (await params in Next.js 14+) required careful attention.
   - Prisma Client Singleton: In development, Next.js hot-reloads modules, which can create
     multiple Prisma Client instances. Resolved with the standard globalThis caching pattern
     to ensure a single instance.
   - .gitignore Conflict: The root repository's .gitignore had a lib/ rule that blocked
     src/lib/prisma.js from being tracked. Resolved with git add -f to force-add the file.
   - Date Handling: Prisma's DateTime type stores dates as ISO strings internally. Converting
     between JavaScript Date objects and the API's YYYY-MM-DD string format required explicit
     new Date() wrapping on input and careful timezone handling.

b. Prompting (what required additional guidance; what worked poorly/well):
   - Effective strategy: Schema-first development — defining the Prisma schema first, then
     generating API routes, then building the frontend. This mirrors the natural workflow
     of Prisma-based projects.
   - What worked well: Reusing the component structure from the Express+React version. Since
     both use React, the component logic (SummaryCards, Charts, etc.) transferred almost
     directly — only the import paths and API call patterns changed.
   - What required guidance: The Prisma aggregation for the summary endpoint needed specific
     instructions. Prisma's groupBy API is less intuitive than Django's annotate() or raw SQL
     GROUP BY, so I opted for fetching transactions and aggregating in JavaScript instead.
   - Next.js's "use client" directive needed explicit mention — without it, components using
     React hooks (useState, useEffect) would fail with server component errors.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run (dev server starts, page loads): ~12 minutes
   - Time to full CRUD functionality: ~30 minutes
   - Time to charts and filtering: ~40 minutes total
   - Note: Fastest overall thanks to component reuse from Version #2 and Next.js's unified
     project structure (no separate server/client setup)
```
