# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS146S Study repository - A collaborative course assignment submission system for Stanford's CS146S (The Modern Software Developer) focusing on AI/LLM integration and modern Python development.

## Build and Development Commands

All commands run from within a week directory that has a Makefile (weeks 4-7):

```bash
make run      # Start FastAPI server (http://localhost:8000, docs at /docs)
make test     # Run pytest
make format   # Run black + ruff --fix
make lint     # Run ruff check
make seed     # Initialize/seed SQLite database
```

Environment setup:
```bash
conda create -n cs146s python=3.12 -y && conda activate cs146s
poetry install --no-interaction
```

Pre-commit (optional):
```bash
pre-commit install
pre-commit run --all-files
```

## Architecture

**Backend Pattern (weeks 4-7):**
```
FastAPI → Routers → Services → SQLAlchemy Models
                 ↓
              Pydantic Schemas
```

- `backend/app/main.py` - FastAPI app entry point
- `backend/app/db.py` - SQLAlchemy engine/session setup
- `backend/app/models.py` - ORM models with TimestampMixin
- `backend/app/schemas.py` - Pydantic v2 request/response validation
- `backend/app/routers/` - Endpoint handlers (notes, action_items)
- `backend/app/services/` - Business logic (e.g., LLM extraction)
- `frontend/` - Static HTML/JS/CSS served from FastAPI's `/static`
- `data/` - SQLite database and `seed.sql`

**Key patterns:**
- Dependency injection via `Depends(get_db)` for sessions
- Pagination (`skip`, `limit`), sorting (`sort` with `-` prefix for desc), search (`q`)
- PATCH endpoints for partial updates
- HTTP 201 for creation, proper error status codes

## Code Style

Configured in `pyproject.toml`:
- **Line length:** 100 characters
- **Formatter:** black
- **Linter:** ruff (rules: E, F, I, UP, B)
- **Python:** 3.10+ (3.12 recommended)

## Week Structure

| Week | Focus |
|------|-------|
| 1 | LLM prompting techniques (CoT, RAG, Tool Calling, Reflexion) |
| 2-3 | First full-stack app, MCP servers |
| 4-7 | Progressive full-stack (notes + action items) with increasing features |
| 8 | Multi-stack replication (MERN, Django, Rails, etc.) |

## Submission Workflow

1. Branch: `git checkout -b week{N}-{initials}`
2. Copy: `cp -r week{N} submissions/{initials}/`
3. Work in: `submissions/{initials}/week{N}/`
4. Commit: `git commit -m "[Week{N} - {initials}] 과제 완료"`
5. PR title: `[Week{N} - {initials}]`

## Environment Variables

Copy `.env.example` to `.env` and configure:
```bash
OPENAI_API_KEY=     # OpenAI API access
ANTHROPIC_API_KEY=  # Anthropic/Claude API access
GEMINI_API_KEY=     # Google Gemini API access
```

## Key Dependencies

- FastAPI + uvicorn (web)
- SQLAlchemy 2.0+ (ORM)
- Pydantic 2.0+ (validation)
- google-genai (Gemini API for LLM)
- pytest + httpx (testing)
