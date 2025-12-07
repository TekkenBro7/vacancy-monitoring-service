from datetime import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    user_id: int
    vacancy_id: int


class BookmarkRead(BaseModel):
    id: int
    user_id: int
    vacancy_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
