"""
Notes router for creating and retrieving notes.

Refactored: Uses Pydantic schemas for request/response validation.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..schemas import NoteCreate, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


# -----------------------------------------------------------------------------
# Note Endpoints (Refactored: Pydantic schemas + proper status codes)
# -----------------------------------------------------------------------------


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate) -> NoteResponse:
    """
    Create a new note.

    Args:
        payload: NoteCreate schema with content field

    Returns:
        NoteResponse with the created note details
    """
    note_id = db.insert_note(payload.content.strip())
    note = db.get_note(note_id)
    return NoteResponse(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    """
    List all notes.

    Returns:
        List of NoteResponse objects
    """
    rows = db.list_notes()
    return [
        NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Get a single note by ID.

    Args:
        note_id: The note ID to retrieve

    Returns:
        NoteResponse with the note details

    Raises:
        HTTPException: 404 if note not found
    """
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])


