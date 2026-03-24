# Bolt Blog

A modern blog application built with **React + TypeScript + Tailwind CSS** frontend and **Express + TypeScript + SQLite** backend. Generated in the style of [bolt.new](https://bolt.new/).

## Tech Stack

- **Backend:** TypeScript / Express / better-sqlite3
- **Frontend:** React / Vite / TypeScript / Tailwind CSS
- **Database:** SQLite

## Prerequisites

- Node.js 18+

## Setup & Run

### 1. Server

```bash
cd server
npm install
npm run dev
```

Server runs on [http://localhost:5001](http://localhost:5001).

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

## Features

- Create, read, update, and delete blog posts
- Full-text search across titles, content, author, and tags
- Tag support (comma-separated)
- Modern, responsive UI with Tailwind CSS
- TypeScript throughout (client + server)
- Loading states and animations
- Client-side routing with React Router
