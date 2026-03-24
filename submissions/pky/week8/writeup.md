# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **kunyoung** \
SUNet ID: **mindlogic12345** \
Citations: **Claude Code, bolt.new**

This assignment took me about **4** hours to do.


## App Concept
```
Notes & Action Items Manager — a full-stack CRUD application for managing personal notes and
action items. Users can create, view, search, and update notes (title + content). They can also
create action items (description), mark them as completed, reopen them, and filter by completion
status. The app features search functionality for notes, sorting by various fields, and pagination.
Data is persisted in a SQLite database across all three versions.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: version1-django
AI app generation platform: Claude Code
Tech Stack: Python (Django) + Vanilla JavaScript
Persistence: SQLite (Django default)
Frameworks/Libraries Used: Django 4.2, Django REST Framework
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   Django REST Framework requires explicit configuration for search/filter/sort since it
   doesn't provide them out of the box with function-based views. Implemented custom query
   parameter parsing in the view functions to handle q, sort, skip, limit, and completed
   filter parameters manually, matching the FastAPI reference implementation.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   Claude Code handled the Django scaffolding well. The main guidance needed was ensuring
   the API URL prefix (/api/) matched the frontend expectations and that the DRF views
   returned proper status codes (201 for creation). Translating the SQLAlchemy models to
   Django ORM was straightforward.

c. Approximate time-to-first-run and time-to-feature metrics:
   Time-to-first-run: ~15 minutes (scaffold + migrate + basic views)
   Time-to-full-feature: ~45 minutes (all CRUD + search + sort + frontend)
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: version2-express-react
AI app generation platform: Claude Code
Tech Stack: Node.js (Express) + React + SQLite
Persistence: SQLite via better-sqlite3
Frameworks/Libraries Used: Express 4, React 18, Vite 5, better-sqlite3, cors
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   The main challenge was setting up the Vite proxy configuration to forward /api requests
   to the Express backend during development. Also needed to handle the synchronous nature
   of better-sqlite3 (vs async ORMs), which actually simplified the route handlers. CORS
   configuration was needed for development mode.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   Claude Code generated the Express backend and React components efficiently. The component
   decomposition (NoteForm, NoteList, ActionItemForm, ActionItemList) worked well for
   maintainability. The centralized api.js module kept fetch logic clean.

c. Approximate time-to-first-run and time-to-feature metrics:
   Time-to-first-run: ~20 minutes (backend + frontend scaffold + proxy setup)
   Time-to-full-feature: ~1 hour (all components + API integration + styling)
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: version3-bolt
AI app generation platform: bolt.new
Tech Stack: TypeScript (Next.js) + Prisma + SQLite
Persistence: SQLite via Prisma ORM
Frameworks/Libraries Used: Next.js 14 (App Router), Prisma 5, React 18, TypeScript 5
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   bolt.new generated a solid initial scaffold but required minor fixes: Prisma client
   singleton pattern for development hot-reloading, proper Next.js API route handler
   signatures (using NextRequest/NextResponse), and ensuring the Prisma schema used
   correct SQLite-compatible column mappings.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   The initial bolt.new prompt needed to be very specific about the exact models, API
   endpoints, and UI features. Vague prompts led to incomplete implementations. Including
   the exact field names, query parameters, and UI interactions in the prompt produced
   much better results.

c. Approximate time-to-first-run and time-to-feature metrics:
   Time-to-first-run: ~10 minutes (bolt.new generation + npm install + prisma migrate)
   Time-to-full-feature: ~30 minutes (generation + manual fixes + testing)
```
