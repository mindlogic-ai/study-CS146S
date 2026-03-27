
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True


class ExtractionResult(BaseModel):
    action_items: list[str]
    tags: list[str]
