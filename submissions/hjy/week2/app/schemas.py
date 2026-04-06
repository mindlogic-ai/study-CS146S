"""Pydantic v2 schemas for request/response validation (TODO 3 - Refactor)."""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- Note schemas ---


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Note text content")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


# --- Action Item schemas ---


class ActionItemResponse(BaseModel):
    id: int
    text: str
    done: bool = False


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = False


class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemResponse]


class MarkDoneRequest(BaseModel):
    done: bool = True
