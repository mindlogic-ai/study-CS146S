from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _check_not_blank(v: str) -> str:
    if not v.strip():
        raise ValueError("must not be blank")
    return v


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

    @field_validator("title", "content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        return _check_not_blank(v)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = None

    @field_validator("title", "content")
    @classmethod
    def not_blank(cls, v: str | None) -> str | None:
        if v is not None:
            return _check_not_blank(v)
        return v


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)

    @field_validator("description")
    @classmethod
    def not_blank(cls, v: str) -> str:
        return _check_not_blank(v)


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

    @field_validator("description")
    @classmethod
    def not_blank(cls, v: str | None) -> str | None:
        if v is not None:
            return _check_not_blank(v)
        return v
