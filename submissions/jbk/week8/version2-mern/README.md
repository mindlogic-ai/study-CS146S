# Version 2: MERN Stack (MongoDB + Express + React + Node.js)

## Tech Stack
- **Backend:** Node.js / Express.js
- **Frontend:** React (Vite)
- **Database:** MongoDB

## Prerequisites
- Node.js 18+
- MongoDB (local install or Docker)

### MongoDB Setup (choose one)

**Option A: Docker**
```bash
docker run -d -p 27017:27017 --name mongo mongo:7
```

**Option B: Homebrew (macOS)**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

## Installation & Setup

```bash
# Install server dependencies
cd server
cp .env.example .env   # edit if needed
npm install

# Seed sample data
npm run seed

# Install client dependencies
cd ../client
npm install
```

## Run (Development)

```bash
# Terminal 1: Start backend
cd server
npm run dev

# Terminal 2: Start frontend
cd client
npm run dev
```

Visit http://localhost:3000

## Run (Production)

```bash
# Build client
cd client
npm run build

# Start server (serves built client)
cd ../server
npm start
```

Visit http://localhost:5001

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notes | List notes (query: q, skip, limit, sort) |
| POST | /api/notes | Create note |
| GET | /api/notes/:id | Get note |
| PATCH | /api/notes/:id | Update note |
| GET | /api/action-items | List items (query: completed, skip, limit, sort) |
| POST | /api/action-items | Create item |
| GET | /api/action-items/:id | Get item |
| PATCH | /api/action-items/:id | Update item |
| PUT | /api/action-items/:id/complete | Mark complete |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MONGODB_URI | mongodb://localhost:27017/notesapp | MongoDB connection string |
| PORT | 5001 | Server port |
