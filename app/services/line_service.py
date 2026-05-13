import base64
import hashlib
import hmac

import httpx

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"


def verify_line_signature(body: bytes, signature: str, channel_secret: str) -> bool:
    expected = base64.b64encode(
        hmac.new(channel_secret.encode(), body, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)


async def send_line_reply(reply_token: str, message: str, access_token: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(
            LINE_REPLY_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "replyToken": reply_token,
                "messages": [{"type": "text", "text": message}],
            },
        )
