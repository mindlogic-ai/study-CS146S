# Week 2 – Action Item Extractor

A FastAPI + SQLite application that converts free-form notes into enumerated action items using both heuristic parsing and LLM-powered extraction via Google Gemini.

## Project Overview

This application provides a simple yet powerful interface for extracting action items from unstructured notes. It supports two extraction strategies:

- **Heuristic-based extraction**: Identifies action items using pattern matching (bullet points, keywords, checkbox markers)
- **LLM-powered extraction**: Uses Google Gemini to intelligently extract action items from natural language text

The application stores notes and action items in a SQLite database and includes a single-page frontend for easy interaction.

## Tech Stack

- **Backend**: FastAPI with uvicorn
- **Database**: SQLite
- **Validation**: Pydantic v2
- **LLM Integration**: Google Gemini API (google-genai)
- **Testing**: pytest with httpx
- **Python**: 3.10+ (3.12 recommended)

## Setup and Installation

### Prerequisites

Ensure you have conda and Python 3.10+ installed on your system.

### Environment Setup

1. Activate the conda environment:
   ```bash
   conda activate cs146s
   ```

2. Install dependencies from the project root:
   ```bash
   poetry install --no-interaction
   ```

### Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Add your Google Gemini API key to the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

   Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com).

## Running the Application

From the project root directory, start the FastAPI server:

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at:
- **Frontend**: http://127.0.0.1:8000/
- **API Docs**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative Docs**: http://127.0.0.1:8000/redoc (ReDoc)

The `--reload` flag enables auto-reload during development. For production, omit this flag.

## API Endpoints

### Notes

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/notes` | Create a new note | `NoteCreate` | `NoteRead` (201) |
| GET | `/notes` | List all notes | - | `list[NoteRead]` |
| GET | `/notes/{note_id}` | Get a single note | - | `NoteRead` |

**NoteCreate**:
```json
{
  "content": "string (required)"
}
```

**NoteRead**:
```json
{
  "id": "integer",
  "content": "string",
  "created_at": "ISO 8601 datetime"
}
```

### Action Items

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| POST | `/action-items/extract` | Extract action items (heuristic) | `ExtractRequest` | `ExtractResponse` (201) |
| POST | `/action-items/extract-llm` | Extract action items (LLM) | `ExtractRequest` | `ExtractResponse` (201) |
| GET | `/action-items` | List all action items | `?note_id=id` (optional) | `list[ActionItemRead]` |
| POST | `/action-items/{action_item_id}/done` | Mark action item as done/undone | `MarkDoneRequest` | `MarkDoneResponse` |

**ExtractRequest**:
```json
{
  "text": "string (required)",
  "save_note": "boolean (default: false)"
}
```

**ExtractResponse**:
```json
{
  "note_id": "integer or null",
  "items": [
    {
      "id": "integer",
      "text": "string",
      "done": "boolean",
      "created_at": "ISO 8601 datetime or null"
    }
  ]
}
```

**MarkDoneRequest**:
```json
{
  "done": "boolean (default: true)"
}
```

**MarkDoneResponse**:
```json
{
  "id": "integer",
  "done": "boolean"
}
```

### Query Parameters

- **List action items**: Add `?note_id={id}` to filter by note ID
  ```bash
  curl http://localhost:8000/action-items?note_id=1
  ```

## Extraction Methods

### Heuristic Extraction (`/action-items/extract`)

The heuristic-based extractor identifies action items using pattern matching:

- **Bullet points**: Lines starting with `-`, `*`, `•`, or numbers (e.g., `1.`)
- **Keyword prefixes**: Lines starting with `todo:`, `action:`, or `next:`
- **Checkboxes**: Lines containing `[ ]` or `[todo]`
- **Imperative sentences**: Sentences starting with action verbs (add, create, implement, fix, update, write, check, verify, refactor, document, design, investigate)

If no patterns match, the extractor falls back to splitting text by sentence boundaries and identifying imperative-sounding statements.

### LLM Extraction (`/action-items/extract-llm`)

The LLM-powered extractor uses Google Gemini 2.0 Flash to intelligently identify action items from natural language. This method is more flexible and can understand context-dependent action items that heuristics might miss.

**Note**: Requires `GEMINI_API_KEY` to be set in `.env`.

## Frontend

The single-page frontend (`frontend/index.html`) includes:

- **Text input area** for entering notes
- **Extract (Heuristic)** button to extract using pattern matching
- **Extract (LLM)** button to extract using Gemini
- **List Notes** button to display all stored notes
- **Action items checklist** with checkboxes to mark items as done/undone

The frontend automatically updates with results and syncs with the backend API.

## Testing

Run the test suite from the project root:

```bash
poetry run pytest week2/tests/ -v
```

### Test Coverage

Tests are located in `week2/tests/test_extract.py` and cover:

- Heuristic extraction with various input patterns (bullet lists, keywords, checkboxes)
- LLM extraction with multiple note types
- Edge cases (empty input, duplicate items, mixed formats)

### Running Specific Tests

```bash
# Run a specific test function
poetry run pytest week2/tests/test_extract.py::test_extract_action_items -v

# Run tests matching a pattern
poetry run pytest week2/tests/ -k "llm" -v
```

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point with lifespan handler
│   ├── db.py                # SQLite database layer
│   ├── schemas.py           # Pydantic v2 models for request/response validation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── notes.py         # Notes CRUD endpoints
│   │   └── action_items.py  # Action item extraction and management endpoints
│   └── services/
│       └── extract.py       # Heuristic and LLM extraction logic
├── frontend/
│   └── index.html           # Single-page application frontend
├── tests/
│   ├── __init__.py
│   └── test_extract.py      # Unit tests for extraction functions
├── data/                    # SQLite database (auto-created on first run)
├── assignment.md            # Assignment requirements and TODOs
├── writeup.md               # Implementation writeup and documentation
└── README.md                # This file
```

## Database

The SQLite database is automatically initialized on application startup via the `lifespan` handler in `main.py`. The database file is stored in the `data/` directory and includes two main tables:

- **notes**: Stores original note content with timestamps
- **action_items**: Stores extracted action items with done status and timestamps

## Error Handling

The API returns appropriate HTTP status codes:

- **201 Created**: Successful extraction or creation
- **400 Bad Request**: Missing or invalid input (e.g., empty text)
- **404 Not Found**: Requested resource not found (e.g., note or action item ID)
- **500 Internal Server Error**: Extraction failed (check logs for details)

All errors include a `detail` field with a human-readable message.

## Logging

The application logs extraction failures to help with debugging. Check the console or application logs when extraction encounters issues.

## Development Tips

### Hot Reload

The `--reload` flag enables FastAPI's auto-reload feature. Changes to Python files will automatically restart the server.

### API Documentation

Interactive API documentation is available at `http://127.0.0.1:8000/docs`. Use this to test endpoints directly without writing code.

### Database Reset

To reset the database, delete the `data/` directory:

```bash
rm -rf week2/data/
```

The database will be recreated on the next application startup.

### Environment Variables

Additional environment variables can be added to `.env`:

```bash
OPENAI_API_KEY=     # Optional: for alternative LLM integrations
ANTHROPIC_API_KEY=  # Optional: for alternative LLM integrations
```

## Example Usage

### Extract Action Items (Heuristic)

```bash
curl -X POST http://localhost:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "- Set up database\n- Write unit tests\n- Update documentation",
    "save_note": true
  }'
```

**Response**:
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Set up database", "done": false, "created_at": "2024-01-15T10:30:00"},
    {"id": 2, "text": "Write unit tests", "done": false, "created_at": "2024-01-15T10:30:00"},
    {"id": 3, "text": "Update documentation", "done": false, "created_at": "2024-01-15T10:30:00"}
  ]
}
```

### Extract Action Items (LLM)

```bash
curl -X POST http://localhost:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We need to implement user authentication, set up automated testing, and write API documentation before launch.",
    "save_note": true
  }'
```

### List All Notes

```bash
curl http://localhost:8000/notes
```

### Mark Action Item as Done

```bash
curl -X POST http://localhost:8000/action-items/1/done \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

## Troubleshooting

### Gemini API Errors

If you encounter LLM extraction errors:

1. Verify `GEMINI_API_KEY` is set in `.env`
2. Check that your API key is valid and has sufficient quota
3. Ensure your network connection is stable

### Database Errors

If the database becomes corrupted or you encounter schema issues:

1. Delete the `data/` directory
2. Restart the application to reinitialize the database

### Port Already in Use

If port 8000 is already in use:

```bash
poetry run uvicorn week2.app.main:app --reload --port 8001
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Google Generative AI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
