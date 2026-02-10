"""Notes router — refactored with Pydantic schemas (TODO 3) and GET /notes (TODO 4)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


# TODO 4: List all notes endpoint
@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[dict]:
    rows = db.list_notes()
    return [
        {"id": r["id"], "content": r["content"], "created_at": r["created_at"]} for r in rows
    ]


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate) -> dict:
    note_id = db.insert_note(payload.content.strip())
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="Failed to create note")
    return {"id": note["id"], "content": note["content"], "created_at": note["created_at"]}


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> dict:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return {"id": row["id"], "content": row["content"], "created_at": row["created_at"]}
