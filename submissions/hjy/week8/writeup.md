# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Hyungjoon** \
Citations: Claude Code (AI assistant for V1 and V2 development), bolt.new (AI app generation for V3)

This assignment took me about **5** hours to do.


## App Concept
```
Notes & Action Items — a personal productivity app for managing notes and to-do items.

Main features:
- Notes: Create, read, update, and delete notes with a title and content. Search notes by title or content.
- Action Items: Create, read, update, and delete action items. Toggle completion status (complete/reopen). Filter by completed status.
- Timestamps: All items display creation dates.
- Validation: Required fields enforced with user-facing error messages.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: v1-django
AI app generation platform: Claude Code
Tech Stack: Django (Python) + Vanilla JavaScript
Persistence: SQLite
Frameworks/Libraries Used: Django 5.x, Django REST Framework 3.x
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Django's CSRF middleware was removed from the middleware stack to
     simplify API requests from the vanilla JS frontend, since the app
     runs locally without authentication.
   - Django's static file serving needed STATICFILES_DIRS configured
     to point to the frontend/ directory.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Claude Code handled the Django + DRF setup well with minimal prompting.
   - Had to specify the exact API endpoint paths to match the frontend JS.
   - DRF ViewSets made CRUD implementation very concise compared to
     writing each view manually.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~15 minutes (project setup, models, migrations, runserver)
   - Time to full feature: ~45 minutes (API endpoints + frontend)
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: v2-mern
AI app generation platform: Claude Code
Tech Stack: MERN (MongoDB, Express.js, React, Node.js)
Persistence: MongoDB
Frameworks/Libraries Used: Express.js, Mongoose, React 18, Vite
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - MongoDB needed to be running locally before starting the backend.
     Used MongoDB Atlas as a fallback by setting MONGODB_URI in .env.
   - Vite proxy configuration was needed to forward /api requests to
     the Express backend on port 3001.
   - React state management for inline editing required careful handling
     of edit mode toggling per item.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - The MERN stack is well-documented, so Claude Code generated clean
     code with standard patterns (Mongoose schemas, Express router, React components).
   - Needed to specify ES modules (import/export) instead of CommonJS (require)
     for the backend.
   - Component separation (Notes.jsx, ActionItems.jsx) kept the code organized.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~10 minutes (npm install, start backend + frontend)
   - Time to full feature: ~40 minutes (API routes + React components)
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: v3-bolt
AI app generation platform: bolt.new
Tech Stack: React + TypeScript + Supabase (PostgreSQL)
Persistence: Supabase (hosted PostgreSQL)
Frameworks/Libraries Used: React 18, TypeScript, Vite, Tailwind CSS, Supabase JS SDK, Lucide React (icons)
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Supabase required creating a project and running the SQL migration
     manually to set up tables. The generated migration file made this
     straightforward.
   - Row Level Security (RLS) policies needed to be set to allow public
     access since the app has no authentication.
   - Environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
     had to be configured in .env before the app could connect to the database.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - bolt.new generated a complete, well-structured app from a single prompt
     describing the features.
   - The generated UI (Tailwind CSS + Lucide icons) looked polished out of
     the box — significantly better than the manually-built versions.
   - bolt.new chose Supabase for persistence automatically, which added a
     cloud dependency but simplified backend code (no separate server needed).
   - Search filtering was implemented client-side rather than via Supabase
     queries, which is fine for small datasets but wouldn't scale well.
   - Action items lack inline description editing — only completion toggle
     and delete are supported. Adding an edit button with a textarea
     (similar to the Notes component's pattern) would complete the CRUD.
   - Error messages are generic ("Failed to create note") and don't
     surface the actual Supabase error details. Including the error
     message from the API response would improve debuggability.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~5 minutes (bolt.new generation + Supabase setup)
   - Time to full feature: ~15 minutes (including Supabase table creation and env config)
```
