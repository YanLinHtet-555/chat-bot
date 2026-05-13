import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    bot_name: Mapped[str] = mapped_column(String(100), default="Assistant")
    vertical: Mapped[str] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # LINE channel credentials
    line_channel_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    line_channel_access_token: Mapped[str] = mapped_column(Text, nullable=True)

    # Messenger credentials
    messenger_page_access_token: Mapped[str] = mapped_column(Text, nullable=True)
    messenger_verify_token: Mapped[str] = mapped_column(String(255), nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="tenant")
