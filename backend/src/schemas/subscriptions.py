from datetime import datetime

from pydantic import BaseModel


class SubscriptionTargetCreate(BaseModel):
    name: str


class SubscriptionTargetRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionTargetUpdate(BaseModel):
    name: str | None = None


class SubscriptionTypeCreate(BaseModel):
    name: str
    description: str | None = None


class SubscriptionTypeRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SubscriptionCreate(BaseModel):
    user_id: int
    subscription_type_id: int
    target_type_id: int


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    subscription_type_id: int
    target_type_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionUpdate(BaseModel):
    subscription_type_id: int | None = None
    target_type_id: int | None = None
