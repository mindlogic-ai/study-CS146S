"""
Pydantic schemas for API request/response validation.

This module defines well-typed API contracts for all endpoints,
replacing raw Dict[str, Any] types with validated models.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Note Schemas
# -----------------------------------------------------------------------------

class NoteCreate(BaseModel):
    """Request schema for creating a note."""
    content: str = Field(..., min_length=1, description="Note content text")


class NoteResponse(BaseModel):
    """Response schema for a note."""
    id: int
    content: str
    created_at: str


# -----------------------------------------------------------------------------
# Action Item Schemas
# -----------------------------------------------------------------------------

class ActionItemResponse(BaseModel):
    """Response schema for an action item."""
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool = False
    created_at: Optional[str] = None


class ActionItemExtract(BaseModel):
    """Extracted action item (id + text only)."""
    id: int
    text: str


class ExtractRequest(BaseModel):
    """Request schema for extracting action items."""
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ExtractResponse(BaseModel):
    """Response schema for extraction results."""
    note_id: Optional[int] = None
    items: List[ActionItemExtract]


class MarkDoneRequest(BaseModel):
    """Request schema for marking an action item as done/pending."""
    done: bool = Field(default=True, description="Completion status")


class MarkDoneResponse(BaseModel):
    """Response schema for mark done operation."""
    id: int
    done: bool
