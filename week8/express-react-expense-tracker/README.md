# Expense Tracker — Express + React

개인 가계부 웹 앱 (Express + React 버전)

## Prerequisites

- Node.js 18+

## Setup

```bash
# Install server dependencies
cd server
npm install

# Install client dependencies
cd ../client
npm install

# Seed database
cd ../server
npm run seed
```

## Run

Terminal 1 (server):
```bash
cd server
npm start
```

Terminal 2 (client):
```bash
cd client
npm run dev
```

Open http://localhost:5173

## Tech Stack

- Backend: Express.js
- Frontend: React (Vite) + Recharts
- Database: SQLite (better-sqlite3)
