# MERN Blog

A blog application built with the **MERN** stack (MongoDB, Express, React, Node.js).

## Tech Stack

- **Backend:** Node.js / Express
- **Frontend:** React (Vite) / React Router
- **Database:** MongoDB (Mongoose ODM)

## Prerequisites

- Node.js 18+
- MongoDB (local or [MongoDB Atlas](https://www.mongodb.com/atlas))

## Setup & Run

### 1. Server

```bash
cd server
cp .env.example .env    # Edit MONGODB_URI if needed
npm install
npm run dev
```

Server runs on [http://localhost:5000](http://localhost:5000).

### 2. Client

```bash
cd client
npm install
npm run dev
```

Client runs on [http://localhost:5173](http://localhost:5173). API calls are proxied to the server.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | List all posts (supports `?q=` search) |
| POST | `/api/posts` | Create a new post |
| GET | `/api/posts/:id` | Get a single post |
| PUT | `/api/posts/:id` | Update a post |
| DELETE | `/api/posts/:id` | Delete a post |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017/mern-blog` | MongoDB connection string |
| `PORT` | `5000` | Server port |

## Features

- Create, read, update, and delete blog posts
- Search posts by keyword
- Tag support (stored as array in MongoDB)
- Client-side routing with React Router
- Responsive UI
