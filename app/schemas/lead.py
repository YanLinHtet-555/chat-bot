import uuid
from datetime import datetime

from pydantic import BaseModel


class LeadCreate(BaseModel):
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    interest: str | None = None
    budget: str | None = None
    qualification_score: int = 0


class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    interest: str | None = None
    budget: str | None = None
    qualification_score: int | None = None
    status: str | None = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str | None
    email: str | None
    phone: str | None
    interest: str | None
    budget: str | None
    qualification_score: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
