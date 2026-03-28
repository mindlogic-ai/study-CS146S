"""
Action Items router for extracting and managing action items.

Refactored: Uses Pydantic schemas for request/response validation.
Added: LLM-based extraction endpoint using Gemini API.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, status

from .. import db
from ..schemas import (
    ActionItemExtract,
    ActionItemResponse,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


# -----------------------------------------------------------------------------
# Extraction Endpoints (Refactored: Pydantic schemas + added LLM endpoint)
# -----------------------------------------------------------------------------


@router.post("/extract", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract(payload: ExtractRequest) -> ExtractResponse:
    """
    Extract action items from text using rule-based extraction.

    Args:
        payload: ExtractRequest with text and save_note flag

    Returns:
        ExtractResponse with optional note_id and extracted items
    """
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text.strip())

    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)

    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemExtract(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    """
    Extract action items from text using LLM (Google Gemini API).

    This endpoint uses natural language understanding to extract
    action items from free-form text, including natural language sentences.

    Args:
        payload: ExtractRequest with text and save_note flag

    Returns:
        ExtractResponse with optional note_id and extracted items
    """
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text.strip())

    items = extract_action_items_llm(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)

    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemExtract(id=i, text=t) for i, t in zip(ids, items)],
    )


# -----------------------------------------------------------------------------
# Action Item Management Endpoints (Refactored: Pydantic schemas)
# -----------------------------------------------------------------------------


@router.get("", response_model=List[ActionItemResponse])
def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:
    """
    List all action items, optionally filtered by note_id.

    Args:
        note_id: Optional filter to get items for a specific note

    Returns:
        List of ActionItemResponse objects
    """
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    """
    Mark an action item as done or pending.

    Args:
        action_item_id: The action item ID to update
        payload: MarkDoneRequest with done status

    Returns:
        MarkDoneResponse with updated status
    """
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)


