# Action Item Extractor

A FastAPI-based web application that extracts actionable tasks from free-form text notes. Supports both heuristic-based and LLM-powered (Gemini API) extraction.

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI app entry point with lifespan
│   ├── db.py                # SQLite database layer
│   ├── schemas.py           # Pydantic v2 request/response models
│   ├── routers/
│   │   ├── notes.py         # /notes endpoints
│   │   └── action_items.py  # /action-items endpoints
│   └── services/
│       └── extract.py       # Heuristic & LLM extraction logic
├── frontend/
│   └── index.html           # Single-page HTML/JS frontend
├── tests/
│   └── test_extract.py      # Unit tests for extraction functions
├── data/                    # SQLite database (auto-created)
├── pyproject.toml
└── .python-version
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Install dependencies
uv sync

# Create .env file with your Gemini API key (required for LLM extraction)
echo "GEMINI_API_KEY=your-key-here" > .env
```

### Running the Server

```bash
uv run uvicorn app.main:app --reload --app-dir .
```

The app will be available at:
- **Frontend:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/{note_id}` | Get a single note by ID |

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | Extract action items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract action items using Gemini LLM |
| `GET` | `/action-items` | List all action items (optionally filter by `?note_id=`) |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/undone |

### Example Requests

**Extract (heuristic):**
```bash
curl -X POST http://localhost:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "- Set up database\n- Write tests", "save_note": true}'
```

**Extract (LLM):**
```bash
curl -X POST http://localhost:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{"text": "We need to fix the login bug and deploy to staging.", "save_note": false}'
```

## Running Tests

```bash
uv run pytest tests/ -v
```

The LLM extraction tests use mocked Gemini API responses, so no API key is needed to run the test suite.
