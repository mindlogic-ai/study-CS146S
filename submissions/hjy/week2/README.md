# Action Item Extractor

A FastAPI-based web application that converts free-form notes into structured, actionable task items. Supports both heuristic-based and LLM-powered (Google Gemini) extraction.

## Project Overview

This application allows users to:
- Paste meeting notes or free-form text
- Extract action items using **heuristic rules** (regex-based bullet/keyword detection)
- Extract action items using **LLM** (Google Gemini API with structured JSON output)
- Save notes and track action item completion via checkboxes

## Setup

### Prerequisites
- Python 3.10+ (3.12 recommended)
- [Conda](https://docs.conda.io/) for environment management
- [Poetry](https://python-poetry.org/) for dependency management
- A Google Gemini API key

### Installation

```bash
# Create and activate conda environment
conda create -n cs146s python=3.12 -y
conda activate cs146s

# Install dependencies (from project root)
poetry install --no-interaction

# Configure environment variables
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

### Running the Server

```bash
# From the project root
poetry run uvicorn submissions.hjy.week2.app.main:app --reload
```

Open http://127.0.0.1:8000/ in your browser.

## API Endpoints

### Notes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/notes` | List all notes |
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes/{note_id}` | Get a single note by ID |

### Action Items

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/action-items/extract` | Extract action items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract action items using Gemini LLM |
| `GET` | `/action-items` | List all action items (optional `?note_id=` filter) |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/undone |

Interactive API documentation is available at http://127.0.0.1:8000/docs (Swagger UI).

## Running Tests

```bash
# Run all tests
poetry run pytest submissions/hjy/week2/tests/ -v

# Run only heuristic tests (no API key required)
poetry run pytest submissions/hjy/week2/tests/test_extract.py::test_extract_bullets_and_checkboxes -v

# Run LLM tests (requires GEMINI_API_KEY)
poetry run pytest submissions/hjy/week2/tests/test_extract.py::TestExtractActionItemsLLM -v
```

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **Database**: SQLite (via `sqlite3` module)
- **Validation**: Pydantic v2
- **LLM**: Google Gemini API (`google-genai`)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Testing**: pytest
