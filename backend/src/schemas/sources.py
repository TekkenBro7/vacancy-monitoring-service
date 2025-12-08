from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SourceTypeCreate(BaseModel):
    type_name: str
    description: str | None = None


class SourceTypeRead(BaseModel):
    id: int
    type_name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceTypeUpdate(BaseModel):
    type_name: str | None = None
    description: str | None = None


class SourceCreate(BaseModel):
    name: str
    source_url: HttpUrl
    source_type_id: int


class SourceRead(BaseModel):
    id: int
    name: str
    source_url: str
    source_type_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceUpdate(BaseModel):
    name: str | None = None
    source_url: HttpUrl | None = None
    source_type_id: int | None = None
