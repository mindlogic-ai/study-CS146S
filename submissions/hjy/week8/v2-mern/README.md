# Notes & Action Items - MERN Stack

A full-stack CRUD application built with MongoDB, Express, React, and Node.js.

## Prerequisites

- Node.js 18+
- MongoDB (local or remote)

## Setup

### Backend

```bash
cd backend
npm install
```

Create a `.env` file (optional):

```env
MONGODB_URI=mongodb://localhost:27017/notesapp
PORT=3001
```

If no `.env` is provided, the app defaults to `mongodb://localhost:27017/notesapp` on port `3001`.

Start the server:

```bash
npm run dev    # development (auto-restart on changes)
npm start      # production
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the backend at `http://localhost:3001`.

## API Endpoints

### Notes

| Method | Endpoint         | Description                      |
|--------|------------------|----------------------------------|
| GET    | /api/notes       | List notes (supports `?q=` search) |
| POST   | /api/notes       | Create a note                    |
| GET    | /api/notes/:id   | Get a single note                |
| PATCH  | /api/notes/:id   | Partial update a note            |
| DELETE | /api/notes/:id   | Delete a note                    |

### Action Items

| Method | Endpoint              | Description                                  |
|--------|-----------------------|----------------------------------------------|
| GET    | /api/action-items     | List items (supports `?completed=true/false`) |
| POST   | /api/action-items     | Create an action item                        |
| PATCH  | /api/action-items/:id | Partial update (including complete/reopen)   |
| DELETE | /api/action-items/:id | Delete an action item                        |

## Tech Stack

- **Frontend**: React 18 + Vite
- **Backend**: Express.js + Mongoose
- **Database**: MongoDB
