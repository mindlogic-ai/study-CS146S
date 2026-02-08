from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemRead,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse, status_code=201)
def extract(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items(text)
    except Exception:
        logger.exception("Heuristic extraction failed")
        raise HTTPException(status_code=500, detail="extraction failed")

    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemRead(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm", response_model=ExtractResponse, status_code=201)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items_llm(text)
    except Exception:
        logger.exception("LLM extraction failed")
        raise HTTPException(status_code=500, detail="LLM extraction failed")

    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemRead(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("", response_model=list[ActionItemRead])
def list_all(note_id: int | None = None) -> list[ActionItemRead]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemRead(
            id=r["id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)
