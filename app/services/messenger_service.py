import hashlib
import hmac

import httpx

MESSENGER_API_URL = "https://graph.facebook.com/v19.0/me/messages"


def verify_messenger_signature(body: bytes, signature: str, app_secret: str) -> bool:
    expected = "sha256=" + hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def send_messenger_reply(recipient_id: str, message: str, page_access_token: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(
            MESSENGER_API_URL,
            params={"access_token": page_access_token},
            json={
                "recipient": {"id": recipient_id},
                "message": {"text": message},
            },
        )
