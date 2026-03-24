# Week 8 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Minseo Kim** \
SUNet ID: **idk**\
Citations: **Claude Code (AI assistant used for code generation and scaffolding)**

This assignment took me about **3** hours to do.

## App Concept

```
Notes & Action Items Manager - A productivity web application for managing notes and tasks.

Main features:
- Notes: Create, read, update, and delete notes with title and content fields.
  Search functionality to filter notes by title or content.
- Action Items: Create, read, update, and delete action items (tasks) with descriptions.
  Mark items as completed or incomplete with toggle functionality.
  Filter view to show only completed items.
- All records have automatic timestamps (created_at, updated_at).
- Persistent storage with database backend.
- Clean, responsive single-page UI with inline editing.
```

## Version #1 Description

```
APP DETAILS:
===============
Folder name: version-django
AI app generation platform: Claude Code
Tech Stack: Python (Django) + Vanilla JavaScript
Persistence: SQLite (via Django ORM)
Frameworks/Libraries Used: Django 6.x, Django REST Framework, django-cors-headers, Vanilla HTML/CSS/JS
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Django 6.x is very new; DRF works seamlessly with it.
   - Serving the frontend required configuring both TEMPLATES_DIRS and STATICFILES_DIRS
     in settings.py so that the index.html template could reference static assets.
   - CSRF middleware needed to be considered for API calls; using DRF's
     SessionAuthentication was avoided in favor of simple unauthenticated API access
     for development simplicity.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Django's convention-over-configuration approach meant less prompting was needed
     for the backend structure. ModelSerializer and ModelViewSet provided CRUD out of
     the box with minimal code.
   - The frontend required more manual work since it's vanilla JS without a framework.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~5 minutes (project scaffold + migrate)
   - Time to full CRUD: ~20 minutes
   - Time to complete with frontend: ~30 minutes
```

## Version #2 Description

```
APP DETAILS:
===============
Folder name: version-mern
AI app generation platform: Claude Code
Tech Stack: MongoDB + Express.js + React + Node.js (MERN)
Persistence: MongoDB (in-memory via mongodb-memory-server for zero-config local development)
Frameworks/Libraries Used: Express.js, Mongoose, React 19, Vite, cors, concurrently
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - MongoDB setup can be complex; using mongodb-memory-server eliminated the need
     for a local MongoDB installation entirely.
   - Vite proxy configuration was needed to forward /api requests from the React
     dev server (port 3000) to the Express backend (port 5000).
   - React components needed careful state management for inline editing
     (tracking editId, editTitle, editContent separately).

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Express route structure is straightforward but requires explicit error handling
     in every route handler (try/catch blocks).
   - Mongoose schemas with timestamps:true auto-generate createdAt/updatedAt fields,
     which simplified the model definitions.
   - React component structure was clean with useState/useCallback hooks.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~5 minutes (npm install + server start)
   - Time to full CRUD: ~25 minutes
   - Time to complete with React frontend: ~35 minutes
```

## Version #3 Description

```
APP DETAILS:
===============
Folder name: version-nextjs
AI app generation platform: bolt.new
Tech Stack: Next.js 13 (App Router) + React 18 + Supabase + shadcn/ui + Tailwind CSS
Persistence: Supabase (hosted PostgreSQL with Row Level Security)
Frameworks/Libraries Used: Next.js 13, React 18, TypeScript, @supabase/supabase-js, shadcn/ui (Radix UI), Tailwind CSS, Lucide React
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - bolt.new scaffolded a full shadcn/ui component library (40+ components),
     most of which are unused. This is typical of AI generators - they over-provision
     to cover potential needs.
   - Supabase requires creating tables and RLS policies via SQL migration before
     the app can function. The generated migration file handled this well.
   - The "use client" directive was correctly placed on page components that use
     React hooks, showing bolt.new understands the App Router client/server boundary.
   - Exporting code from bolt.new required a custom Node.js script since there is
     no built-in download/export feature in the platform.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - bolt.new generated the entire project from a single prompt describing the app
     concept, data models, and desired features. The initial output was functional.
   - It chose Supabase for persistence (rather than the Prisma + SQLite I might have
     chosen manually), which is a reasonable production-ready choice.
   - The shadcn/ui component library gives a polished UI out of the box with minimal
     CSS work needed. bolt.new integrates well with modern React UI libraries.
   - No CORS or proxy configuration needed since Next.js API routes and pages share
     the same origin.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time to first run: ~2 minutes (bolt.new generates and runs instantly in-browser)
   - Time to full CRUD: ~5 minutes (single prompt generated all CRUD operations)
   - Time to complete (including export and local setup): ~15 minutes
```