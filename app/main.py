from fastapi import FastAPI

from app.config import settings
from app.routers import admin, appointments, chat, leads, tenants
from app.routers import webhook_line, webhook_messenger

app = FastAPI(
    title="AI Automation Agency Chatbot",
    version="0.1.0",
    docs_url="/docs" if settings.app_env == "development" else None,
)

app.include_router(chat.router)
app.include_router(tenants.router)
app.include_router(appointments.router)
app.include_router(leads.router)
app.include_router(admin.router)
app.include_router(webhook_line.router)
app.include_router(webhook_messenger.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
