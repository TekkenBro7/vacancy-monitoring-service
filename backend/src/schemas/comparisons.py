from datetime import datetime

from pydantic import BaseModel


class ComparisonCreate(BaseModel):
    name: str
    user_id: int


class ComparisonRead(BaseModel):
    id: int
    name: str
    user_id: int
    vacancies: list[int] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComparisonUpdate(BaseModel):
    name: str | None = None
