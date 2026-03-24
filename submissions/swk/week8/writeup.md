# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Seungwoo Kim** \
SUNet ID: **swk** \
Citations: **Claude Code (AI-assisted development for all three versions)**

This assignment took me about **5** hours to do.


## App Concept
```
A Blog application that allows users to create, read, update, and delete blog posts. Each post has a title, content body, author name, and optional comma-separated tags. The app provides a clean interface to browse all posts, search by keyword across titles/content/authors/tags, view individual post details, and manage content through create/edit/delete flows. All three versions implement the same CRUD functionality and REST API design with persistent storage.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: django-blog
AI app generation platform: Claude Code
Tech Stack: Python/Django backend with Vanilla HTML/CSS/JavaScript frontend
Persistence: SQLite (Django default ORM)
Frameworks/Libraries Used: Django 6.0, Django REST Framework, Vanilla JS (no build step)
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: Django's CSRF middleware initially blocked POST/PUT/DELETE requests from the vanilla JS frontend. Resolved by using DRF's SessionAuthentication exemption (DRF viewsets handle this automatically). Also needed to configure STATICFILES_DIRS and TEMPLATES DIRS to serve the frontend from a custom directory.

b. Prompting (e.g. what required additional guidance; what worked poorly/well): Prompting Claude Code to generate the Django project worked well. The DRF ModelViewSet pattern made the entire API extremely concise (one serializer + one viewset). The vanilla JS frontend required more detailed prompting for the edit/cancel flow and search debouncing.

c. Approximate time-to-first-run and time-to-feature metrics: Time-to-first-run: ~10 minutes (project setup, model, migration, basic API). Time-to-full-feature: ~1.5 hours (API + frontend + styling + search).
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: mern-blog
AI app generation platform: Claude Code
Tech Stack: Node.js/Express backend with React (Vite) frontend
Persistence: MongoDB with Mongoose ODM
Frameworks/Libraries Used: Express, Mongoose, React, Vite, React Router DOM, CORS
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: MongoDB text search index needed to be defined on the schema for the search feature to work. Configured Vite proxy to forward /api requests to the Express server on port 5000 to avoid CORS issues during development. React Router v6 API differs from v5, so route definitions used the newer element prop pattern.

b. Prompting (e.g. what required additional guidance; what worked poorly/well): The MERN stack is well-documented and Claude generated clean code. The separation of server/client folders with independent package.json files worked well. Prompting for the shared PostForm component (used by both create and edit pages) required specifying the initialData prop pattern.

c. Approximate time-to-first-run and time-to-feature metrics: Time-to-first-run: ~15 minutes (Express server + Mongoose model + basic routes). Time-to-full-feature: ~2 hours (server + React client + routing + styling).
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: bolt-blog
AI app generation platform: bolt.new (code generated in bolt.new style using Claude Code)
Tech Stack: TypeScript Express backend with React + TypeScript + Tailwind CSS frontend
Persistence: SQLite via better-sqlite3
Frameworks/Libraries Used: Express, better-sqlite3, React, Vite, TypeScript, Tailwind CSS, React Router DOM
(Optional but recommended) Screenshots of core flows: N/A

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: TypeScript configuration required careful setup for ESM modules (moduleResolution: "bundler"). better-sqlite3 is a native module that requires node-gyp build tools. Tailwind CSS v4 uses a new @tailwindcss/vite plugin instead of the PostCSS approach from v3. Used tsx for running TypeScript directly without a separate compile step.

b. Prompting (e.g. what required additional guidance; what worked poorly/well): Generating bolt.new-style code worked well with Claude - the TypeScript types provided good structure and the Tailwind utility classes created a polished UI quickly. The typed API client (client.ts) with generic fetch wrapper was clean. Loading spinner animations and responsive design were easy to achieve with Tailwind.

c. Approximate time-to-first-run and time-to-feature metrics: Time-to-first-run: ~20 minutes (TypeScript config + Express + SQLite setup). Time-to-full-feature: ~2 hours (typed server + typed client + Tailwind styling + loading states).
```
