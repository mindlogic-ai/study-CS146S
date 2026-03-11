from __future__ import annotations

from pydantic import BaseModel


# --- Notes ---
class NoteCreate(BaseModel):
    content: str


class NoteRead(BaseModel):
    id: int
    content: str
    created_at: str


# --- Action Items ---
class ActionItemRead(BaseModel):
    id: int
    text: str
    done: bool = False
    created_at: str | None = None


# --- Extraction ---
class ExtractRequest(BaseModel):
    text: str
    save_note: bool = False


class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemRead]


# --- Mark Done ---
class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
