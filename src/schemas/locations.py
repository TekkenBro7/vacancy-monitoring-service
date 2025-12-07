from datetime import datetime

from pydantic import BaseModel


class CountryCreate(BaseModel):
    name: str


class CountryRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CountryUpdate(BaseModel):
    name: str | None = None


class CityCreate(BaseModel):
    name: str
    description: str | None = None
    country_id: int


class CityRead(BaseModel):
    id: int
    name: str
    description: str | None
    country_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CityUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    country_id: int | None = None
