# Week 2 – Action Item Extractor

A FastAPI + SQLite application that converts free-form notes into structured, actionable checklist items. Supports both rule-based heuristic extraction and LLM-powered extraction via the Google Gemini API.

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI entry point with lifespan
│   ├── db.py                # SQLite database helpers
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── notes.py         # CRUD endpoints for notes
│   │   └── action_items.py  # Extraction & action-item endpoints
│   └── services/
│       └── extract.py       # Heuristic + LLM extraction logic
├── frontend/
│   └── index.html           # Single-page HTML/JS frontend
├── tests/
│   └── test_extract.py      # Unit tests for extraction functions
├── data/                    # SQLite database (auto-created)
├── assignment.md
├── writeup.md
└── README.md
```

## Setup

### Prerequisites
- Python 3.12 (via Conda recommended)
- A Google Gemini API key

### Installation

```bash
# Create and activate conda environment
conda create -n cs146s python=3.12 -y
conda activate cs146s

# Install dependencies
poetry install --no-interaction

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Server

From the **project root**:

```bash
poetry run uvicorn submissions.jhs.week2.app.main:app --reload
```

Then open http://127.0.0.1:8000/ in your browser.

## API Endpoints

### Notes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes (newest first) |
| `GET` | `/notes/{note_id}` | Get a single note by ID |

### Action Items

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/action-items/extract` | Extract items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract items using Gemini LLM |
| `GET` | `/action-items` | List all action items (optionally filter by `?note_id=`) |
| `POST` | `/action-items/{id}/done` | Toggle an action item's done status |

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract-llm \
  -H 'Content-Type: application/json' \
  -d '{"text": "- Set up database\ntodo: Write tests", "save_note": true}'
```

## Running Tests

```bash
poetry run python -m pytest submissions/jhs/week2/tests/ -v
```

Tests use `unittest.mock` to mock the Gemini API, so no API key is needed to run the test suite.
