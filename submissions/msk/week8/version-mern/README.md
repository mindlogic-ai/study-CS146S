# Notes & Action Items - MERN Version

A full-stack Notes & Action Items manager built with MongoDB, Express, React, and Node.js.

## Tech Stack

- **Backend:** Node.js, Express.js
- **Frontend:** React 19 (Vite)
- **Database:** MongoDB (in-memory via mongodb-memory-server for easy local setup)
- **ORM:** Mongoose

## Prerequisites

- Node.js 18+
- npm

## Setup & Run

```bash
# Install all dependencies (server + client)
npm run install-all

# Start both server and client (concurrently)
npm run dev
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5001/api

### Run separately

```bash
# Server only (port 5001)
npm run server

# Client only (port 3000, proxies API to 5001)
npm run client
```

## API Endpoints

| Method | Endpoint                  | Description            |
|--------|---------------------------|------------------------|
| GET    | /api/notes                | List all notes         |
| POST   | /api/notes                | Create a note          |
| GET    | /api/notes/:id            | Get a note             |
| PATCH  | /api/notes/:id            | Update a note          |
| DELETE | /api/notes/:id            | Delete a note          |
| GET    | /api/action-items         | List all action items  |
| POST   | /api/action-items         | Create an action item  |
| GET    | /api/action-items/:id     | Get an action item     |
| PATCH  | /api/action-items/:id     | Update an action item  |
| DELETE | /api/action-items/:id     | Delete an action item  |

### Query Parameters

- Notes: `?q=search_term` for search, `?sort=field` or `?sort=-field` for sorting
- Action Items: `?completed=true` to filter by completion status

## Known Issues

- Uses mongodb-memory-server: data is lost when the server restarts
- No authentication (development mode only)
