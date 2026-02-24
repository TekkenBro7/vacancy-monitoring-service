from datetime import datetime

from pydantic import BaseModel


class SkillCreate(BaseModel):
    name: str


class SkillRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillUpdate(BaseModel):
    name: str | None = None


class SkillReadSimple(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
