# Action Item Extractor

A FastAPI + SQLite web application that converts free-form notes into enumerated, actionable checklist items. Supports both heuristic-based and LLM-powered (Gemini) extraction.

## Setup

### Prerequisites

- Python 3.10+ (3.12 recommended)
- [Conda](https://docs.conda.io/) for environment management
- [Poetry](https://python-poetry.org/) for dependency management

### Installation

```bash
# Create and activate conda environment
conda create -n cs146s python=3.12 -y
conda activate cs146s

# Install dependencies
poetry install --no-interaction

# Copy environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Server

```bash
poetry run uvicorn week2.app.main:app --reload
```

Open http://127.0.0.1:8000/ in your browser.

## API Endpoints

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all saved notes |
| `GET` | `/notes/{note_id}` | Retrieve a specific note |

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | Extract action items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract action items using Gemini LLM |
| `GET` | `/action-items` | List all action items (optional `?note_id=` filter) |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/undone |

Interactive API docs available at http://127.0.0.1:8000/docs.

## Running Tests

```bash
poetry run pytest week2/tests/ -v
```

Tests use mocked Gemini API responses, so no API key is needed to run them.

## Project Structure

```
week2/
├── app/
│   ├── main.py            # FastAPI app entry point with lifespan
│   ├── db.py              # SQLite database layer
│   ├── schemas.py         # Pydantic v2 request/response models
│   ├── routers/
│   │   ├── notes.py       # Notes CRUD endpoints
│   │   └── action_items.py # Extraction and management endpoints
│   └── services/
│       └── extract.py     # Heuristic + LLM extraction logic
├── frontend/
│   └── index.html         # Single-page HTML/JS frontend
├── tests/
│   └── test_extract.py    # Unit tests for extraction functions
└── data/
    └── app.db             # SQLite database (auto-created)
```
