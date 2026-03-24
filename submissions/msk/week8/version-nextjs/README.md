# Notes & Action Items Manager - Next.js + Supabase (bolt.new)

A full-stack Notes & Action Items manager built with Next.js 13, Supabase, shadcn/ui, and Tailwind CSS. Generated using [bolt.new](https://bolt.new).

## Prerequisites

- Node.js 18+
- npm
- A Supabase project (free tier works)

## Environment Configuration

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Fill in your Supabase credentials:

   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

   You can find these in your Supabase project dashboard under Settings &gt; API.

## Database Setup

Run the SQL migration in `supabase/migrations/` against your Supabase project:

1. Go to your Supabase dashboard &gt; SQL Editor
2. Paste the contents of `supabase/migrations/20260324041456_create_notes_and_action_items_tables.sql`
3. Click "Run"

This creates the `notes` and `action_items` tables with Row Level Security policies.

## Installation & Run

```bash
npm install
npm run dev
```

The app will be available at http://localhost:3000.

## Tech Stack

- **Framework:** Next.js 13 (App Router)
- **Frontend:** React 18, TypeScript, Tailwind CSS, shadcn/ui
- **Database:** Supabase (PostgreSQL)
- **Icons:** Lucide React

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /api/notes | List all notes (supports `?q=search_term`) |
| POST | /api/notes | Create a note |
| GET | /api/notes/:id | Get a single note |
| PATCH | /api/notes/:id | Update a note |
| DELETE | /api/notes/:id | Delete a note |
| GET | /api/action-items | List action items (supports `?completed=true`) |
| POST | /api/action-items | Create an action item |
| GET | /api/action-items/:id | Get a single action item |
| PATCH | /api/action-items/:id | Update an action item |
| DELETE | /api/action-items/:id | Delete an action item |

## Known Issues

- No authentication; all data is publicly accessible via Supabase RLS policies.
- Requires an active Supabase project for persistence (no local-only mode).
- The bolt.new scaffolding includes many unused shadcn/ui components; only a subset are actively used.