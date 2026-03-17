
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteCreate, NotePatch, NoteRead
from ..services.extract import extract_action_items

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    if payload.tag_ids:
        tags = db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all()
        if len(tags) != len(payload.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        note.tags = list(tags)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.tag_ids is not None:
        tags = db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all()
        if len(tags) != len(payload.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        note.tags = list(tags)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/count")
def count_notes(
    db: Session = Depends(get_db),
    q: str | None = None,
) -> dict:
    stmt = select(func.count(Note.id))
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))
    total = db.execute(stmt).scalar()
    return {"count": total}


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int = Path(..., gt=0), db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.post("/{note_id}/extract-actions")
def extract_actions_from_note(
    note_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> list[dict]:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return extract_action_items(note.content)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int = Path(..., gt=0), db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()
