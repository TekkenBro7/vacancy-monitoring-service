from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CommentAuthor(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    vacancy_id: int
    content: str = Field(..., min_length=1, max_length=2000)
    rating: int | None = Field(None, ge=1, le=5)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class CommentRead(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    content: str
    rating: int | None
    created_at: datetime
    updated_at: datetime
    user: CommentAuthor | None = None

    model_config = {"from_attributes": True}


class CommentUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=2000)
    rating: int | None = Field(None, ge=1, le=5)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
