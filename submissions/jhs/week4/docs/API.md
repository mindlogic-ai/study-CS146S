# API Reference

Auto-generated from source. Last synced: 2026-02-24

## Endpoints

### Notes

| Method | Path | Description | Request Body | Response | Status |
|--------|------|-------------|-------------|----------|--------|
| GET | `/notes/` | List all notes | — | `NoteRead[]` | 200 |
| POST | `/notes/` | Create a new note | `NoteCreate` | `NoteRead` | 201 |
| GET | `/notes/search/?q=` | Search notes by title/content | — | `NoteRead[]` | 200 |
| GET | `/notes/{note_id}` | Get a single note | — | `NoteRead` | 200/404 |
| PATCH | `/notes/{note_id}` | Partially update a note | `NoteUpdate` | `NoteRead` | 200/400/404 |
| DELETE | `/notes/{note_id}` | Delete a note | — | — | 204/404 |
| POST | `/notes/{note_id}/extract` | Extract action items & tags from note | — | `ExtractResult` | 200/404 |

### Action Items

| Method | Path | Description | Request Body | Response | Status |
|--------|------|-------------|-------------|----------|--------|
| GET | `/action-items/` | List all action items | — | `ActionItemRead[]` | 200 |
| POST | `/action-items/` | Create a new action item | `ActionItemCreate` | `ActionItemRead` | 201 |
| PUT | `/action-items/{item_id}/complete` | Mark item as complete | — | `ActionItemRead` | 200/404 |
| DELETE | `/action-items/{item_id}` | Delete an action item | — | — | 204/404 |

## Schemas

### NoteCreate
| Field | Type | Constraints |
|-------|------|-------------|
| title | string | required, min 1, max 200 chars |
| content | string | required, min 1 char |

### NoteUpdate
| Field | Type | Constraints |
|-------|------|-------------|
| title | string \| null | optional, min 1, max 200 chars |
| content | string \| null | optional, min 1 char |

### NoteRead
| Field | Type |
|-------|------|
| id | integer |
| title | string |
| content | string |

### ActionItemCreate
| Field | Type | Constraints |
|-------|------|-------------|
| description | string | required, min 1 char |

### ActionItemRead
| Field | Type |
|-------|------|
| id | integer |
| description | string |
| completed | boolean |

### ExtractResult
| Field | Type |
|-------|------|
| action_items | string[] |
| tags | string[] |
