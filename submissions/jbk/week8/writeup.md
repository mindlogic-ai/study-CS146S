# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Jeongbin Kim** \
SUNet ID: **jbk** \
Citations: **Claude Code, Bolt.new**

This assignment took me about **3** hours to do.


## App Concept
```
A "Notes & Action Items" productivity app. Users can create and manage notes
(with title and content) and action items (with description and completion status).
Features include full CRUD operations, search across notes by title/content,
filtering action items by completion status, sortable and paginated lists,
and persistent database storage. The app provides a clean single-page UI with
two main sections: Notes and Action Items.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: version1-django
AI app generation platform: Claude Code
Tech Stack: Python / Django / Django REST Framework / Vanilla JavaScript
Persistence: SQLite (Django default)
Frameworks/Libraries Used: Django 5.x, Django REST Framework, Vanilla HTML/CSS/JS
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Django REST Framework requires django.contrib.auth in INSTALLED_APPS even
     when not using authentication. Resolved by adding it to settings.
   - Had to handle CSRF exemption for API views since DRF's APIView handles this
     by default with SessionAuthentication disabled.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Claude Code generated the entire Django project structure, models, serializers,
     views, and URLs in one pass. The frontend was ported from Week 7 with minimal
     changes (API prefix changed from / to /api/).
   - Worked well: specifying the exact Week 7 API contract ensured feature parity.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time-to-first-run: ~5 minutes (scaffolding + migrations + seed)
   - Time-to-full-feature: ~15 minutes
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: version2-mern
AI app generation platform: Claude Code
Tech Stack: MongoDB / Express.js / React / Node.js (MERN)
Persistence: MongoDB
Frameworks/Libraries Used: Express 4.x, Mongoose 8.x, React 18, Vite 6, cors, dotenv
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - MongoDB needs to be installed separately (via Docker or Homebrew).
     Documented both options in README.
   - Mongoose uses _id instead of id, so frontend components reference n._id
     instead of n.id.
   - Vite proxy configuration needed to forward /api requests to Express backend.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Claude Code created the Express server, Mongoose models, routes, and React
     components. The React components follow a clean separation of concerns with
     api.js as a fetch wrapper.
   - Worked well: the Vite + React setup compiled without errors on first build.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time-to-first-run: ~10 minutes (npm install for both server and client)
   - Time-to-full-feature: ~20 minutes
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: version3-bolt
AI app generation platform: Bolt.new
Tech Stack: React 18 + TypeScript + Tailwind CSS (Vite) / Supabase Edge Functions (Deno) / PostgreSQL
Persistence: Supabase PostgreSQL
Frameworks/Libraries Used: React 18, TypeScript, Tailwind CSS 3.x, Vite 5, Supabase JS SDK, lucide-react icons, Deno (Edge Functions)
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
   - Bolt chose Supabase as the backend, which requires a Supabase account and project
     setup (creating tables via SQL migration, deploying Edge Functions).
   - Environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY) must be configured
     before the app can connect to the backend.
   - No major code issues — Bolt generated a working app on the first attempt.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
   - Provided a single detailed prompt specifying data models, API endpoints, frontend UI
     structure, and seed data. Bolt generated the full app in one pass.
   - Worked well: the detailed API contract in the prompt resulted in correct Edge Function
     implementations matching the expected endpoints.
   - Bolt automatically chose a modern stack (React + TypeScript + Tailwind + Supabase)
     without needing to specify frameworks.

c. Approximate time-to-first-run and time-to-feature metrics:
   - Time-to-generation: ~2 minutes (Bolt generated all code)
   - Time-to-first-run: ~5 minutes (Supabase project setup + env config + npm install)
   - Time-to-full-feature: ~10 minutes total
```
