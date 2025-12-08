from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    role_id: int | None = None
