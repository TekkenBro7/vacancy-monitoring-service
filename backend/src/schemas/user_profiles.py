from datetime import datetime

from pydantic import BaseModel


class UserProfileRead(BaseModel):
    id: int
    user_id: int
    full_name: str | None
    phone: str | None
    avatar_url: str | None
    desired_salary: int | None
    desired_position: str | None
    desired_salary_currency_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    desired_salary: int | None = None
    desired_position: str | None = None
    desired_salary_currency_id: int | None = None
