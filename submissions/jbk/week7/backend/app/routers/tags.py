from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import TagCreate, TagRead

router = APIRouter(tags=["tags"])


@router.get("/tags/", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    tags = db.query(Tag).all()
    return [TagRead.model_validate(t) for t in tags]


@router.post("/tags/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> Response:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()
    return Response(status_code=204)


@router.post("/notes/{note_id}/tags/{tag_id}", response_model=TagRead, status_code=200)
def attach_tag_to_note(
    note_id: int, tag_id: int, db: Session = Depends(get_db)
) -> TagRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag not in note.tags:
        note.tags.append(tag)
        db.flush()
    return TagRead.model_validate(tag)


@router.delete("/notes/{note_id}/tags/{tag_id}", status_code=204)
def detach_tag_from_note(
    note_id: int, tag_id: int, db: Session = Depends(get_db)
) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag in note.tags:
        note.tags.remove(tag)
        db.flush()
    return Response(status_code=204)
