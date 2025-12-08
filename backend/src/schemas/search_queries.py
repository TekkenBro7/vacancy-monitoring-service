from datetime import datetime

from pydantic import BaseModel


class SearchQueryCreate(BaseModel):
    user_id: int
    query_text: str


class SearchQueryRead(BaseModel):
    id: int
    user_id: int
    query_text: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SearchQueryUpdate(BaseModel):
    query_text: str | None = None
