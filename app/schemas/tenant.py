import uuid
from datetime import datetime

from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    slug: str
    system_prompt: str
    bot_name: str = "Assistant"
    vertical: str | None = None


class TenantUpdate(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    bot_name: str | None = None
    vertical: str | None = None
    is_active: bool | None = None
    line_channel_secret: str | None = None
    line_channel_access_token: str | None = None
    messenger_page_access_token: str | None = None
    messenger_verify_token: str | None = None


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    bot_name: str
    vertical: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
