"""Pydantic v2 schemas for request/response validation (TODO 3: Refactor)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# --- Request schemas ---


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Note text content")


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to persist the text as a note")


class MarkDoneRequest(BaseModel):
    done: bool = Field(default=True, description="Whether the action item is completed")


# --- Response schemas ---


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemResponse(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: list[ActionItemResponse]


class ActionItemDetail(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str


class MarkDoneResponse(BaseModel):
    id: int
    done: bool
