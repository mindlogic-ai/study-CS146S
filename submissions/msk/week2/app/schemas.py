"""Pydantic request/response schemas for the Action Item Extractor API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


# ---------------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------------

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: bool = False


class ActionItemBrief(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemBrief]


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
