from datetime import datetime

from pydantic import BaseModel, Field

# --- Tag schemas ---


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Note schemas ---


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tag_ids: list[int] = Field(default_factory=list)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    tags: list[TagRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    tag_ids: list[int] | None = None


# --- ActionItem schemas ---


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = Field(None, min_length=1)
    completed: bool | None = None
