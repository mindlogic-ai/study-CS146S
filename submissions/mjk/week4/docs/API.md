# API Documentation

> Auto-generated from OpenAPI spec via `/docs-sync`
> Last synced: 2026-02-24

## Base URL
`http://localhost:8000`

## Endpoints

### Root

#### GET /
- **Summary**: Root
- **Response**: `200`

---

### Notes

#### GET /notes/
- **Summary**: List Notes
- **Response**: `200` - `List[NoteRead]`
  - id: integer
  - title: string
  - content: string

#### POST /notes/
- **Summary**: Create Note
- **Request Body**: `NoteCreate` (required)
  - title: string (required)
  - content: string (required)
- **Response**: `201` - `NoteRead`
- **Error**: `422` - Validation Error

#### GET /notes/search/
- **Summary**: Search Notes
- **Query Parameters**:
  - `q`: string (optional) - search query
- **Response**: `200` - `List[NoteRead]`
- **Error**: `422` - Validation Error

#### GET /notes/{note_id}
- **Summary**: Get Note
- **Path Parameters**:
  - `note_id`: integer (required)
- **Response**: `200` - `NoteRead`
- **Error**: `422` - Validation Error

#### PUT /notes/{note_id}
- **Summary**: Update Note
- **Path Parameters**:
  - `note_id`: integer (required)
- **Request Body**: `NoteCreate` (required)
  - title: string (required)
  - content: string (required)
- **Response**: `200` - `NoteRead`
- **Error**: `422` - Validation Error

#### DELETE /notes/{note_id}
- **Summary**: Delete Note
- **Path Parameters**:
  - `note_id`: integer (required)
- **Response**: `200`
- **Error**: `422` - Validation Error

---

### Action Items

#### GET /action-items/
- **Summary**: List Items
- **Response**: `200` - `List[ActionItemRead]`
  - id: integer
  - description: string
  - completed: boolean

#### POST /action-items/
- **Summary**: Create Item
- **Request Body**: `ActionItemCreate` (required)
  - description: string (required)
- **Response**: `201` - `ActionItemRead`
- **Error**: `422` - Validation Error

#### PUT /action-items/{item_id}/complete
- **Summary**: Complete Item
- **Path Parameters**:
  - `item_id`: integer (required)
- **Response**: `200` - `ActionItemRead`
- **Error**: `422` - Validation Error

---

## Schemas

### NoteCreate
| Field | Type | Required |
|-------|------|----------|
| title | string | yes |
| content | string | yes |

### NoteRead
| Field | Type | Required |
|-------|------|----------|
| id | integer | yes |
| title | string | yes |
| content | string | yes |

### ActionItemCreate
| Field | Type | Required |
|-------|------|----------|
| description | string | yes |

### ActionItemRead
| Field | Type | Required |
|-------|------|----------|
| id | integer | yes |
| description | string | yes |
| completed | boolean | yes |
