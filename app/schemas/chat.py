from pydantic import BaseModel


class ChatRequest(BaseModel):
    tenant_slug: str
    session_id: str
    user_identifier: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    bot_name: str
