"""Action items router — refactored with Pydantic schemas (TODO 3) and LLM endpoint (TODO 4)."""

from __future__ import annotations

from fastapi import APIRouter, status

from .. import db
from ..schemas import ActionItemResponse, ExtractRequest, ExtractResponse, MarkDoneRequest
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract(payload: ExtractRequest) -> dict:
    """Extract action items using heuristic rules."""
    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return {
        "note_id": note_id,
        "items": [{"id": i, "text": t, "done": False} for i, t in zip(ids, items)],
    }


# TODO 4: LLM-powered extraction endpoint
@router.post("/extract-llm", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract_llm(payload: ExtractRequest) -> dict:
    """Extract action items using Gemini LLM."""
    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items_llm(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return {
        "note_id": note_id,
        "items": [{"id": i, "text": t, "done": False} for i, t in zip(ids, items)],
    }


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: int | None = None) -> list[dict]:
    rows = db.list_action_items(note_id=note_id)
    return [
        {"id": r["id"], "text": r["text"], "done": bool(r["done"])}
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> dict:
    db.mark_action_item_done(action_item_id, payload.done)
    return {"id": action_item_id, "done": payload.done}
