from datetime import datetime

from pydantic import BaseModel


class CityCreate(BaseModel):
    name: str
    description: str | None = None


class CityRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
