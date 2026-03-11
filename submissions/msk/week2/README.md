# Action Item Extractor

A FastAPI + SQLite web application that converts free-form notes into enumerated action items. Supports both heuristic-based extraction (regex/keyword matching) and LLM-powered extraction via the Gemini API.

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI app with lifespan-managed DB init
│   ├── db.py                # SQLite database layer
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── action_items.py  # Action item endpoints
│   │   └── notes.py         # Note endpoints
│   └── services/
│       └── extract.py       # Heuristic and LLM extraction logic
├── frontend/
│   └── index.html           # Single-page HTML frontend
├── tests/
│   └── test_extract.py      # Unit tests for extraction functions
└── data/
    └── app.db               # SQLite database (auto-created)
```

## Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- A Gemini API key (for LLM extraction)

### Installation

1. Install dependencies from the project root:

```bash
poetry install
```

2. Create a `.env` file in the project root with your API key:

```
GEMINI_API_KEY=your-key-here
```

### Running the Server

```bash
poetry run uvicorn week2.app.main:app --reload
```

Open http://127.0.0.1:8000/ in a browser.

## API Endpoints

### Notes

| Method | Path             | Description           |
|--------|------------------|-----------------------|
| POST   | `/notes`         | Create a new note     |
| GET    | `/notes`         | List all saved notes  |
| GET    | `/notes/{id}`    | Get a single note     |

**POST /notes** request body:

```json
{ "content": "Meeting notes go here..." }
```

### Action Items

| Method | Path                            | Description                          |
|--------|---------------------------------|--------------------------------------|
| POST   | `/action-items/extract`         | Extract items using heuristics       |
| POST   | `/action-items/extract-llm`     | Extract items using Gemini LLM       |
| GET    | `/action-items?note_id=<id>`    | List action items (optionally by note) |
| POST   | `/action-items/{id}/done`       | Mark an item as done/undone          |

**POST /action-items/extract** and **/extract-llm** request body:

```json
{ "text": "- Set up database\n- Write tests", "save_note": true }
```

Response:

```json
{
  "note_id": 1,
  "items": [
    { "id": 1, "text": "Set up database" },
    { "id": 2, "text": "Write tests" }
  ]
}
```

**POST /action-items/{id}/done** request body:

```json
{ "done": true }
```

## Running Tests

```bash
poetry run pytest week2/tests/ -v
```

Note: The LLM extraction tests (`test_llm_extract_bullet_list`, `test_llm_extract_keyword_prefixed`) call the Gemini API and require a valid `GEMINI_API_KEY` in your `.env` file. The `test_llm_extract_empty_input` test runs without API access since it short-circuits on empty input.
