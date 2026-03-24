# Expense Tracker — Express + React + SQLite

A personal expense tracking web application with a decoupled architecture: Express.js REST API backend and React single-page application frontend. This is the full-JavaScript version of the multi-stack expense tracker project.

## Features

- Create, read, update, and delete income/expense transactions
- Fixed categories for expenses (식비, 교통, 쇼핑, 주거, 여가, 기타) and income (급여, 용돈, 기타수입)
- Monthly summary with total income, total expenses, and net balance
- Interactive charts: category breakdown (pie chart) and income vs. expense comparison (bar chart)
- Filter transactions by month, category, and type
- Responsive single-page UI with component-based architecture

## Prerequisites

- Node.js 18 or higher
- npm (included with Node.js)

## Installation & Setup

```bash
# 1. Install server dependencies
cd server
npm install

# 2. Seed the database with sample data (13 transactions across 2 months)
npm run seed

# 3. Install client dependencies
cd ../client
npm install
```

## Running the Application

You need **two terminals** since the server and client run as separate processes:

**Terminal 1 — API Server (port 3001):**
```bash
cd server
npm start
```

**Terminal 2 — React Dev Server (port 5173):**
```bash
cd client
npm run dev
```

Open your browser and navigate to **http://localhost:5173**

> The Vite dev server proxies all `/api/*` requests to the Express server on port 3001, so the frontend can make API calls without CORS issues during development.

## Project Structure

```
express-react-expense-tracker/
├── server/                        # Express.js API server
│   ├── index.js                   # Server entry point, route definitions
│   ├── db.js                      # SQLite database initialization
│   ├── seed.js                    # Database seeding script
│   └── package.json               # Server dependencies
├── client/                        # React SPA (Vite)
│   ├── index.html                 # Vite entry HTML
│   ├── vite.config.js             # Vite config (proxy, React plugin)
│   ├── src/
│   │   ├── main.jsx               # React entry point
│   │   ├── App.jsx                # Root component (state, API calls)
│   │   ├── App.css                # Global styles
│   │   └── components/
│   │       ├── SummaryCards.jsx    # Income/expense/balance cards
│   │       ├── Charts.jsx         # Recharts pie + bar charts
│   │       ├── TransactionTable.jsx  # Transaction list with actions
│   │       ├── TransactionForm.jsx   # Add/edit modal form
│   │       └── Filters.jsx        # Month/category/type filters
│   └── package.json               # Client dependencies
└── README.md
```

## API Endpoints

| Method | Endpoint                    | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/api/transactions`         | List transactions (query: month, category, type) |
| POST   | `/api/transactions`         | Create a new transaction (returns 201)   |
| PATCH  | `/api/transactions/:id`     | Update a transaction (partial)           |
| DELETE | `/api/transactions/:id`     | Delete a transaction                     |
| GET    | `/api/summary`              | Monthly summary with category breakdown  |
| GET    | `/api/categories`           | List available categories by type        |

## Tech Stack

| Layer      | Technology                     |
|------------|--------------------------------|
| Backend    | Express.js 4.x (Node.js)      |
| Frontend   | React 18 + Vite 5.x           |
| Charts     | Recharts 2.x                  |
| Database   | SQLite (better-sqlite3)        |
| Styling    | Plain CSS (no framework)       |
| Dev Tools  | Vite HMR, API proxy           |

## Architecture Notes

This version uses a **decoupled SPA + API** architecture:

- **Server** (`/server`): Stateless REST API. Uses `better-sqlite3` for synchronous, zero-dependency SQLite access with prepared statements. CORS is enabled for cross-origin requests during development.
- **Client** (`/client`): React SPA bootstrapped with Vite. All state management is done with React hooks (`useState`, `useEffect`). Components are organized by feature responsibility.
- **Communication**: The client communicates with the server exclusively through JSON API calls. Vite's proxy configuration eliminates CORS friction during development.

## Known Issues & Notes

- The server uses `better-sqlite3`, which requires native compilation via `node-gyp`. On macOS, ensure Xcode Command Line Tools are installed. On Windows, the `windows-build-tools` package may be needed.
- In production, the React app should be built (`npm run build`) and served as static files from Express, eliminating the need for two servers.
- The SQLite database file (`data.db`) is created automatically in the `server/` directory on first run.
