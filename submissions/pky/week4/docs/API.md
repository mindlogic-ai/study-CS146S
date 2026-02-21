# Week 4 API Documentation

**Title:** Modern Software Dev Starter (Week 4)
**Version:** 0.1.0
**Base URL:** http://localhost:8000

## Overview

This API provides a note-taking system with AI-powered extraction of action items and tags. Built with FastAPI, SQLAlchemy, and Pydantic v2.

---

## Notes

### List Notes

Retrieve all notes.

**Endpoint:** `GET /notes/`

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline..."
  }
]
```

**Response Schema:** Array of `NoteRead`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `title` | string | Note title |
| `content` | string | Note content |

---

### Create Note

Create a new note.

**Endpoint:** `POST /notes/`

**Request Body:** `NoteCreate`

| Field | Type | Constraints | Required | Description |
|-------|------|-------------|----------|-------------|
| `title` | string | min: 1, max: 200 | Yes | Note title |
| `content` | string | min: 1 | Yes | Note content |

**Example Request:**

```json
{
  "title": "Meeting Notes",
  "content": "Discussed project timeline and next steps."
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "title": "Meeting Notes",
  "content": "Discussed project timeline and next steps."
}
```

**Error Responses:**
- `422 Unprocessable Entity` - Validation error (e.g., empty title/content, title > 200 chars)

---

### Search Notes

Search notes by query string (searches in both title and content).

**Endpoint:** `GET /notes/search/`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | No | Search query |

**Example Request:**

```
GET /notes/search/?q=meeting
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline..."
  }
]
```

**Response Schema:** Array of `NoteRead`

---

### Get Note

Retrieve a single note by ID.

**Endpoint:** `GET /notes/{note_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `note_id` | integer | Note identifier |

**Response:** `200 OK`

```json
{
  "id": 1,
  "title": "Meeting Notes",
  "content": "Discussed project timeline..."
}
```

**Error Responses:**
- `404 Not Found` - Note does not exist
- `422 Unprocessable Entity` - Invalid note_id format

---

### Update Note

Update an existing note (partial update supported).

**Endpoint:** `PUT /notes/{note_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `note_id` | integer | Note identifier |

**Request Body:** `NoteUpdate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string \| null | No | Updated title |
| `content` | string \| null | No | Updated content |

**Example Request:**

```json
{
  "title": "Updated Meeting Notes"
}
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "title": "Updated Meeting Notes",
  "content": "Discussed project timeline..."
}
```

**Error Responses:**
- `404 Not Found` - Note does not exist
- `422 Unprocessable Entity` - Validation error

---

### Delete Note

Delete a note by ID.

**Endpoint:** `DELETE /notes/{note_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `note_id` | integer | Note identifier |

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Note does not exist
- `422 Unprocessable Entity` - Invalid note_id format

---

### Extract Action Items and Tags

Use AI to extract action items and tags from a note's content.

**Endpoint:** `POST /notes/{note_id}/extract`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `note_id` | integer | Note identifier |

**Response:** `200 OK`

```json
{
  "action_items": [
    "Review project timeline",
    "Schedule follow-up meeting"
  ],
  "tags": [
    "meeting",
    "project-planning"
  ]
}
```

**Response Schema:** `ExtractionResult`

| Field | Type | Description |
|-------|------|-------------|
| `action_items` | array[string] | Extracted action items |
| `tags` | array[string] | Extracted tags/keywords |

**Error Responses:**
- `404 Not Found` - Note does not exist
- `422 Unprocessable Entity` - Invalid note_id format

---

## Action Items

### List Action Items

Retrieve all action items.

**Endpoint:** `GET /action-items/`

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "description": "Review project timeline",
    "completed": false
  },
  {
    "id": 2,
    "description": "Schedule follow-up meeting",
    "completed": true
  }
]
```

**Response Schema:** Array of `ActionItemRead`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `description` | string | Action item description |
| `completed` | boolean | Completion status |

---

### Create Action Item

Create a new action item.

**Endpoint:** `POST /action-items/`

**Request Body:** `ActionItemCreate`

| Field | Type | Constraints | Required | Description |
|-------|------|-------------|----------|-------------|
| `description` | string | min: 1 | Yes | Action item description |

**Example Request:**

```json
{
  "description": "Review project timeline"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "description": "Review project timeline",
  "completed": false
}
```

**Error Responses:**
- `422 Unprocessable Entity` - Validation error (e.g., empty description)

---

### Mark Action Item Complete

Mark an action item as completed.

**Endpoint:** `PUT /action-items/{item_id}/complete`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `item_id` | integer | Action item identifier |

**Response:** `200 OK`

```json
{
  "id": 1,
  "description": "Review project timeline",
  "completed": true
}
```

**Error Responses:**
- `404 Not Found` - Action item does not exist
- `422 Unprocessable Entity` - Invalid item_id format

---

## Error Responses

All endpoints may return the following error format:

**422 Unprocessable Entity** - Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

**ValidationError Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `loc` | array[string \| integer] | Error location (path to field) |
| `msg` | string | Human-readable error message |
| `type` | string | Error type identifier |
| `input` | any | (Optional) The input that caused the error |
| `ctx` | object | (Optional) Additional context |

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json
