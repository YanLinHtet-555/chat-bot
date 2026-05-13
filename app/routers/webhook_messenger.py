from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import get_active_tenant, handle_message
from app.services.messenger_service import send_messenger_reply, verify_messenger_signature

router = APIRouter(prefix="/webhook/messenger", tags=["Messenger webhook"])


@router.get("/{tenant_slug}")
async def messenger_verify(tenant_slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Meta calls this endpoint to verify the webhook URL."""
    tenant = await get_active_tenant(db, tenant_slug)
    if not tenant or not tenant.messenger_verify_token:
        raise HTTPException(status_code=404, detail="Tenant not found or Messenger not configured")

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == tenant.messenger_verify_token:
        return PlainTextResponse(content=challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/{tenant_slug}")
async def messenger_webhook(tenant_slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    tenant = await get_active_tenant(db, tenant_slug)
    if not tenant or not tenant.messenger_page_access_token:
        raise HTTPException(status_code=404, detail="Tenant not found or Messenger not configured")

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if signature and not verify_messenger_signature(body, signature, tenant.messenger_page_access_token):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            message = event.get("message", {})
            if not message or message.get("is_echo"):
                continue

            sender_id = event["sender"]["id"]
            user_text = message.get("text", "")
            if not user_text:
                continue

            reply = await handle_message(
                db=db,
                tenant=tenant,
                session_id=f"messenger_{sender_id}",
                user_message=user_text,
                user_identifier=sender_id,
            )

            await send_messenger_reply(sender_id, reply, tenant.messenger_page_access_token)

    return {"status": "ok"}
