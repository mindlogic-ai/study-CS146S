# Expense Tracker — Next.js + Prisma + SQLite

A personal expense tracking web application built with Next.js 14's App Router and Prisma ORM. This is the full-stack React framework version of the multi-stack expense tracker project.

## Features

- Create, read, update, and delete income/expense transactions
- Fixed categories for expenses (식비, 교통, 쇼핑, 주거, 여가, 기타) and income (급여, 용돈, 기타수입)
- Monthly summary with total income, total expenses, and net balance
- Interactive charts: category breakdown (pie chart) and income vs. expense comparison (bar chart)
- Filter transactions by month, category, and type
- Responsive single-page UI with server-side rendering support

## Prerequisites

- Node.js 18 or higher
- npm (included with Node.js)

## Installation & Setup

```bash
# 1. Install dependencies
npm install

# 2. Generate Prisma client and apply database schema
npx prisma db push

# 3. Seed the database with sample data (13 transactions across 2 months)
npm run seed
```

## Running the Application

```bash
npm run dev
```

Open your browser and navigate to **http://localhost:3000**

## Project Structure

```
nextjs-expense-tracker/
├── prisma/
│   ├── schema.prisma              # Database schema (Transaction model)
│   └── seed.js                    # Database seeding script
├── src/
│   ├── app/
│   │   ├── layout.js              # Root layout (HTML shell, metadata)
│   │   ├── page.js                # Main page (client component)
│   │   ├── globals.css            # Global styles
│   │   └── api/
│   │       ├── transactions/
│   │       │   ├── route.js       # GET (list) + POST (create)
│   │       │   └── [id]/
│   │       │       └── route.js   # PATCH (update) + DELETE
│   │       ├── summary/
│   │       │   └── route.js       # GET (monthly aggregation)
│   │       └── categories/
│   │           └── route.js       # GET (fixed category lists)
│   ├── components/
│   │   ├── SummaryCards.jsx       # Income/expense/balance cards
│   │   ├── Charts.jsx            # Recharts pie + bar charts
│   │   ├── TransactionTable.jsx   # Transaction list with actions
│   │   ├── TransactionForm.jsx    # Add/edit modal form
│   │   └── Filters.jsx           # Month/category/type filters
│   └── lib/
│       └── prisma.js              # Prisma client singleton
├── next.config.js                 # Next.js configuration
├── package.json                   # Dependencies and scripts
└── README.md
```

## API Endpoints

| Method | Endpoint                    | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/api/transactions`         | List transactions (query: month, category, type) |
| POST   | `/api/transactions`         | Create a new transaction (returns 201)   |
| PATCH  | `/api/transactions/[id]`    | Update a transaction (partial)           |
| DELETE | `/api/transactions/[id]`    | Delete a transaction                     |
| GET    | `/api/summary`              | Monthly summary with category breakdown  |
| GET    | `/api/categories`           | List available categories by type        |

## Tech Stack

| Layer      | Technology                     |
|------------|--------------------------------|
| Framework  | Next.js 14 (App Router)        |
| Frontend   | React 18                       |
| Charts     | Recharts 2.x                  |
| ORM        | Prisma 5.x                    |
| Database   | SQLite                         |
| Styling    | Plain CSS (no framework)       |

## Architecture Notes

This version uses Next.js 14's **App Router** for a unified full-stack architecture:

- **API Routes** (`/src/app/api/`): File-system based routing. Each route file exports named functions (`GET`, `POST`, `PATCH`, `DELETE`) that handle the corresponding HTTP methods. Uses `NextResponse` for JSON responses.
- **Prisma ORM**: Schema-first database access. The `schema.prisma` file defines the data model, and `prisma generate` creates a type-safe client. A singleton pattern (`src/lib/prisma.js`) prevents multiple client instances during development hot-reload.
- **Client Components**: The main page uses the `"use client"` directive to enable React hooks (`useState`, `useEffect`). Child components are also client components since they handle user interactions.
- **Same-Origin API**: Unlike the Express+React version, there's no CORS configuration needed — the API routes and frontend are served from the same Next.js server.

## Key Differences from Other Versions

| Aspect            | Django              | Express+React          | Next.js (this)          |
|-------------------|---------------------|------------------------|-------------------------|
| Language          | Python              | JavaScript             | JavaScript              |
| Architecture      | Monolithic MVC      | Decoupled SPA + API    | Unified full-stack      |
| ORM               | Django ORM          | Raw SQL (better-sqlite3)| Prisma (schema-first)  |
| Frontend          | Vanilla JS          | React (Vite)           | React (built-in)        |
| Servers needed    | 1                   | 2 (API + Vite)         | 1                       |
| Chart library     | Chart.js (CDN)      | Recharts               | Recharts                |

## Known Issues & Notes

- The Prisma SQLite database file (`prisma/dev.db`) is gitignored and created on `prisma db push`. Run the setup commands before first use.
- The `"use client"` directive is required on any component that uses React hooks or browser APIs. Omitting it causes "useState is not a function" errors.
- For production deployment, run `npm run build` followed by `npm start`. The build step pre-renders static pages and optimizes the bundle.
