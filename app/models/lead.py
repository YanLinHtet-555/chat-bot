import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    interest: Mapped[str] = mapped_column(Text, nullable=True)       # what they're looking for
    budget: Mapped[str] = mapped_column(String(100), nullable=True)
    qualification_score: Mapped[int] = mapped_column(default=0)      # 0-100
    status: Mapped[str] = mapped_column(String(50), default="new")   # new, contacted, qualified, lost
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
