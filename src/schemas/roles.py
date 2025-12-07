from datetime import datetime

from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str


class RoleRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    name: str | None = None
