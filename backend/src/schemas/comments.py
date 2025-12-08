from datetime import datetime

from pydantic import BaseModel, field_validator


class CommentCreate(BaseModel):
    user_id: int
    vacancy_id: int
    content: str
    rating: int

    @field_validator("rating")
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not 0 <= v <= 10:
            raise ValueError("Rating must be between 0 and 10")
        return v


class CommentRead(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    content: str
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentUpdate(BaseModel):
    content: str | None = None
    rating: int | None = None

    @field_validator("rating")
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and not 0 <= v <= 10:
            raise ValueError("Rating must be between 0 and 10")
        return v
