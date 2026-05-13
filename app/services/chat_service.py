from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, Message, Tenant
from app.services.claude import build_history, get_claude_reply


async def get_active_tenant(db: AsyncSession, slug: str) -> Tenant | None:
    result = await db.execute(
        select(Tenant).where(Tenant.slug == slug, Tenant.is_active == True)
    )
    return result.scalar_one_or_none()


async def handle_message(
    db: AsyncSession,
    tenant: Tenant,
    session_id: str,
    user_message: str,
    user_identifier: str | None = None,
) -> str:
    conversation = await _get_or_create_conversation(db, tenant, session_id, user_identifier)
    reply = await get_claude_reply(
        system_prompt=tenant.system_prompt,
        history=build_history(conversation.messages),
        user_message=user_message,
    )
    await _persist_messages(db, conversation.id, user_message, reply)
    return reply


async def _get_or_create_conversation(
    db: AsyncSession,
    tenant: Tenant,
    session_id: str,
    user_identifier: str | None,
) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == tenant.id, Conversation.session_id == session_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        conversation = Conversation(
            tenant_id=tenant.id,
            session_id=session_id,
            user_identifier=user_identifier,
            messages=[],
        )
        db.add(conversation)
        await db.flush()
    return conversation


async def _persist_messages(db: AsyncSession, conversation_id, user_text: str, assistant_text: str) -> None:
    db.add(Message(conversation_id=conversation_id, role="user", content=user_text))
    db.add(Message(conversation_id=conversation_id, role="assistant", content=assistant_text))
    await db.commit()
