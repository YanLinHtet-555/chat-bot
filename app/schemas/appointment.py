import uuid
from datetime import datetime

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID
    customer_name: str
    customer_contact: str
    scheduled_at: datetime
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_name: str
    customer_contact: str
    scheduled_at: datetime
    notes: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
