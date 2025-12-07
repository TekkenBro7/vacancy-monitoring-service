from datetime import datetime

from pydantic import BaseModel


class NotificationTypeCreate(BaseModel):
    name: str
    description: str | None = None


class NotificationTypeRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class NotificationCreate(BaseModel):
    user_id: int
    notification_type_id: int
    message: str | None = None
    subscription_id: int | None = None


class NotificationRead(BaseModel):
    id: int
    user_id: int
    notification_type_id: int
    message: str | None
    subscription_id: int | None
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationUpdate(BaseModel):
    notification_type_id: int | None = None
    message: str | None = None
    subscription_id: int | None = None
    is_read: bool | None = None
