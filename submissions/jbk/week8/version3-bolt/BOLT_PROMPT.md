# Bolt.new Prompt

아래 프롬프트를 bolt.new에 붙여넣으세요:

---

Build a "Notes & Action Items" productivity web app with the following specifications:

DATA MODELS:
1. Note: id, title (string, max 200 chars), content (text), createdAt, updatedAt
2. ActionItem: id, description (text), completed (boolean, default false), createdAt, updatedAt

API ENDPOINTS:
Notes:
- GET /api/notes - list all notes with query params: q (search title+content), skip (offset, default 0), limit (default 50), sort (field name, prefix with - for descending, default -createdAt)
- POST /api/notes - create note with {title, content}, return 201
- GET /api/notes/:id - get single note, 404 if not found
- PATCH /api/notes/:id - partial update (title and/or content)

Action Items:
- GET /api/action-items - list with query params: completed (boolean filter), skip, limit, sort
- POST /api/action-items - create with {description}, return 201
- GET /api/action-items/:id - get single item
- PUT /api/action-items/:id/complete - mark as completed
- PATCH /api/action-items/:id - partial update (description and/or completed)

FRONTEND (Single Page):
1. Notes section:
   - Form to add a note (title + content inputs + Add button)
   - Search input with Search button to filter notes by title/content
   - List of notes showing "title: content"

2. Action Items section:
   - Form to add an action item (description input + Add button)
   - Checkbox to "Show completed only" to filter
   - List showing "description [done/open]" with Complete button (for open items) or Reopen button (for completed items)

STYLING: Clean, modern UI with system fonts, white card sections on light gray background, rounded borders.

DATABASE: Use persistent storage (SQLite or any database). Seed with 2 sample notes ("Welcome" and "Demo") and 2 sample action items ("Try pre-commit" and "Run tests").

---

## 생성 후 할 일
1. Bolt에서 코드 다운로드 (Export/Download)
2. 이 폴더 (`version3-bolt/`)에 코드를 넣기
3. 로컬에서 실행 테스트
4. 안 되는 부분이 있으면 수동 수정하고 README에 기록
5. README.md 작성 (Bolt이 자동 생성했으면 그것을 수정)
