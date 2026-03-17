from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    tags = db.query(Tag).all()
    return [TagRead.model_validate(t) for t in tags]


@router.post("/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    tag = Tag(name=payload.name)
    db.add(tag)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tag name already exists") from exc
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()
