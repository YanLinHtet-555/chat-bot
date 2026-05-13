from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_active_tenant, handle_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    tenant = await get_active_tenant(db, payload.tenant_slug)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or inactive")
    reply = await handle_message(db, tenant, payload.session_id, payload.message, payload.user_identifier)
    return ChatResponse(session_id=payload.session_id, reply=reply, bot_name=tenant.bot_name)
