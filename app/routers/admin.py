import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Conversation, Message, Tenant
from app.schemas.conversation import ConversationResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    tenant_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == tenant_id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/stats/{tenant_id}")
async def tenant_stats(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    conv_count = await db.scalar(
        select(func.count()).where(Conversation.tenant_id == tenant_id)
    )
    msg_count = await db.scalar(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.tenant_id == tenant_id)
    )
    return {
        "tenant": tenant.name,
        "total_conversations": conv_count,
        "total_messages": msg_count,
    }
