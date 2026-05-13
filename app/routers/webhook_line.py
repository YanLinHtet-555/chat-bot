from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import get_active_tenant, handle_message
from app.services.line_service import send_line_reply, verify_line_signature

router = APIRouter(prefix="/webhook/line", tags=["LINE webhook"])


@router.post("/{tenant_slug}")
async def line_webhook(tenant_slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    tenant = await get_active_tenant(db, tenant_slug)
    if not tenant or not tenant.line_channel_secret:
        raise HTTPException(status_code=404, detail="Tenant not found or LINE not configured")

    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_line_signature(body, signature, tenant.line_channel_secret):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()

    for event in payload.get("events", []):
        if event.get("type") != "message":
            continue
        if event["message"].get("type") != "text":
            continue

        user_id = event["source"]["userId"]
        user_text = event["message"]["text"]
        reply_token = event["replyToken"]

        reply = await handle_message(
            db=db,
            tenant=tenant,
            session_id=f"line_{user_id}",
            user_message=user_text,
            user_identifier=user_id,
        )

        await send_line_reply(reply_token, reply, tenant.line_channel_access_token)

    return {"status": "ok"}
