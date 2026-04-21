from datetime import datetime

from pydantic import BaseModel, Field


class CityShort(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserProfileRead(BaseModel):
    id: int
    user_id: int
    full_name: str | None
    phone: str | None
    avatar_url: str | None

    desired_position: str | None
    desired_salary: int | None

    city_id: int | None
    city: CityShort | None = None
    address: str | None

    preferred_remote: bool | None
    preferred_internship: bool | None
    preferred_employment: str | None
    preferred_schedule: str | None

    bio: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None

    desired_position: str | None = None
    desired_salary: int | None = None

    city_id: int | None = None
    address: str | None = None

    preferred_remote: bool | None = None
    preferred_internship: bool | None = None
    preferred_employment: str | None = None
    preferred_schedule: str | None = None

    bio: str | None = Field(None, max_length=1000)


class ProfileOptionsResponse(BaseModel):
    employment_types: list[str]
    schedule_types: list[str]
