# API Documentation

## Notes

### List all notes
- **Method**: GET
- **Path**: `/notes/`
- **Response**: `200 OK` -- `list[NoteRead]`
- **Description**: Returns all notes in the database.

### Create a note
- **Method**: POST
- **Path**: `/notes/`
- **Request body**: `NoteCreate` -- `{ title: string, content: string }`
- **Response**: `201 Created` -- `NoteRead`
- **Description**: Creates a new note with the given title and content.

### Search notes
- **Method**: GET
- **Path**: `/notes/search/`
- **Query params**: `q` (optional string) -- search term to filter by title or content
- **Response**: `200 OK` -- `list[NoteRead]`
- **Description**: Returns notes matching the search query. If no query is provided, returns all notes.

### Get a note by ID
- **Method**: GET
- **Path**: `/notes/{note_id}`
- **Path params**: `note_id` (integer) -- the note's ID
- **Response**: `200 OK` -- `NoteRead`
- **Errors**: `404 Not Found` -- if note does not exist
- **Description**: Returns a single note by its ID.

### Update a note
- **Method**: PUT
- **Path**: `/notes/{note_id}`
- **Path params**: `note_id` (integer) -- the note's ID
- **Request body**: `NoteCreate` -- `{ title: string, content: string }`
- **Response**: `200 OK` -- `NoteRead`
- **Errors**: `404 Not Found` -- if note does not exist; `422 Unprocessable Content` -- if validation fails
- **Description**: Updates the title and content of an existing note.

### Delete a note
- **Method**: DELETE
- **Path**: `/notes/{note_id}`
- **Path params**: `note_id` (integer) -- the note's ID
- **Response**: `204 No Content`
- **Errors**: `404 Not Found` -- if note does not exist
- **Description**: Deletes a note by its ID.

## Action Items

### List all action items
- **Method**: GET
- **Path**: `/action-items/`
- **Response**: `200 OK` -- `list[ActionItemRead]`
- **Description**: Returns all action items in the database.

### Create an action item
- **Method**: POST
- **Path**: `/action-items/`
- **Request body**: `ActionItemCreate` -- `{ description: string }`
- **Response**: `201 Created` -- `ActionItemRead`
- **Description**: Creates a new action item with `completed` defaulting to `false`.

### Complete an action item
- **Method**: PUT
- **Path**: `/action-items/{item_id}/complete`
- **Path params**: `item_id` (integer) -- the action item's ID
- **Response**: `200 OK` -- `ActionItemRead`
- **Errors**: `404 Not Found` -- if action item does not exist
- **Description**: Marks an action item as completed.

## Schemas

### NoteCreate
| Field   | Type   | Constraints                           |
|---------|--------|---------------------------------------|
| title   | string | required, min length 1, max length 200 |
| content | string | required, min length 1                |

### NoteRead
| Field   | Type    | Description       |
|---------|---------|-------------------|
| id      | integer | auto-generated PK |
| title   | string  |                   |
| content | string  |                   |

### ActionItemCreate
| Field       | Type   | Constraints            |
|-------------|--------|------------------------|
| description | string | required, min length 1 |

### ActionItemRead
| Field       | Type    | Description       |
|-------------|---------|-------------------|
| id          | integer | auto-generated PK |
| description | string  |                   |
| completed   | boolean | default: false    |
