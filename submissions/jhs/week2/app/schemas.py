"""TODO 3: Pydantic request/response schemas for well-defined API contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Note schemas ---


class NoteCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="The note text content")


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


# --- Action item schemas ---


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to persist the text as a note")


class ActionItemResponse(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemResponse]


class ActionItemDetail(BaseModel):
    id: int
    note_id: int | None = None
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
