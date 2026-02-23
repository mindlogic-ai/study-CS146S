from typing import Optional

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True
