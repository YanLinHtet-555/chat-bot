# AI Automation Agency Chatbot

A multi-tenant AI chatbot platform built with FastAPI, PostgreSQL, and Groq (LLaMA). Supports LINE, WhatsApp, and Facebook Messenger via webhooks.

## Stack

- **Backend:** Python + FastAPI
- **Database:** PostgreSQL (SQLAlchemy async + Alembic)
- **AI:** Groq API (LLaMA 3.3 70B)
- **Channels:** LINE, WhatsApp (Meta Cloud API), Facebook Messenger
- **Infrastructure:** Docker + Docker Compose

---

## Project Structure

```text
app/
├── main.py                   # FastAPI app entry point
├── config.py                 # Settings from .env
├── database.py               # Async SQLAlchemy engine
├── models/
│   ├── tenant.py             # Client/business model
│   ├── conversation.py       # Chat session model
│   ├── message.py            # Individual messages
│   ├── appointment.py        # Appointment bookings
│   └── lead.py               # Lead qualification
├── routers/
│   ├── chat.py               # POST /chat
│   ├── tenants.py            # CRUD /tenants
│   ├── appointments.py       # /appointments
│   ├── leads.py              # /leads
│   ├── admin.py              # /admin/conversations, /admin/stats
│   ├── webhook_line.py       # LINE webhook
│   └── webhook_messenger.py  # Messenger webhook
├── schemas/                  # Pydantic request/response models
└── services/
    ├── claude.py             # Groq AI integration
    ├── chat_service.py       # Core chat logic
    ├── line_service.py       # LINE API calls
    ├── messenger_service.py  # Messenger API calls
    └── prompts.py            # Pre-built system prompts per vertical
alembic/                      # Database migrations
docker-compose.yml
Dockerfile
requirements.txt
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd chat-bot
copy .env.example .env
```

Fill in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://chatbot:chatbot123@db:5432/chatbot_db
GROQ_API_KEY=your-groq-api-key
APP_ENV=development
SECRET_KEY=your-random-secret
```

Get your free Groq API key at: [console.groq.com](https://console.groq.com)

### 2. Start with Docker

```bash
docker-compose up --build
```

### 3. Run database migrations

```bash
docker-compose exec app alembic revision --autogenerate -m "initial"
docker-compose exec app alembic upgrade head
```

### 4. Open API docs

```
http://localhost:8000/docs
```

---

## Creating a Tenant (Client Bot)

Each client is a **tenant** with their own bot name, system prompt, and channel credentials.

`POST /tenants`:

```json
{
  "name": "Demo Clinic",
  "slug": "demo-clinic",
  "system_prompt": "You are a helpful assistant for a medical clinic. Help patients book appointments and answer questions.",
  "bot_name": "HealthBot",
  "vertical": "clinic"
}
```

Available verticals: `clinic`, `real_estate`, `ecommerce`, `logistics`, `education`

---

## Testing the Chat API

`POST /chat`:

```json
{
  "tenant_slug": "demo-clinic",
  "session_id": "test-session-001",
  "user_identifier": "user123",
  "message": "Hi, I want to book an appointment"
}
```

---

## Channel Setup

### LINE Messaging API

**Prerequisites:**

- LINE account
- LINE Business ID (free): [account.line.biz](https://account.line.biz)

**Steps:**

1. Go to [manager.line.biz](https://manager.line.biz) → create or open your LINE Official Account
2. Go to **Settings → Messaging API → Enable Messaging API**
3. Select your provider → Agree
4. Copy your **Channel Secret** from the Messaging API page
5. Go to [developers.line.biz/console](https://developers.line.biz/console) → open your channel → **Messaging API tab**
6. Click **Issue** under **Channel access token** → copy the token
7. Update your tenant credentials via `PATCH /tenants/{id}`:

```json
{
  "line_channel_secret": "your-channel-secret",
  "line_channel_access_token": "your-access-token"
}
```

8. Expose your server with ngrok:

```bash
ngrok http 8000
```

9. In LINE Official Account Manager → **Settings → Messaging API → Webhook URL**:

```text
https://your-ngrok-url/webhook/line/your-tenant-slug
```

10. Click **Verify** → should say Success
11. Go to **Settings → Response settings**:
    - Turn **Webhooks ON**
    - Turn **Auto-response messages OFF**
12. Scan the QR code from Messaging API page with your LINE app → send a message

---

### Facebook Messenger

**Prerequisites:**

- Facebook account
- Facebook Page (free): [facebook.com/pages/create](https://facebook.com/pages/create)

**Steps:**

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps) → **Create App → Business**
2. On dashboard → find **Messenger → Set up**
3. Under **Messenger → Settings**:
   - Click **Add or Remove Pages** → select your Facebook Page
   - Click **Generate token** → copy the **Page Access Token**
4. Make up a **Verify Token** (any string, e.g. `mysecrettoken123`)
5. Update your tenant via `PATCH /tenants/{id}`:

```json
{
  "messenger_page_access_token": "your-page-access-token",
  "messenger_verify_token": "mysecrettoken123"
}
```

6. Expose your server with ngrok:

```bash
ngrok http 8000
```

7. In Meta Developer Console → **Messenger → Settings → Webhooks → Add Callback URL**:

```text
https://your-ngrok-url/webhook/messenger/your-tenant-slug
```

8. Enter your **Verify Token** → click **Verify and Save**
9. Subscribe to **messages** event
10. Go to your Facebook Page → click **Send Message** → test the bot

---

### WhatsApp (Meta Cloud API)

**Prerequisites:**

- Facebook/Meta account
- Meta Developer App

**Steps:**

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps) → **Create App → Business**
2. On dashboard → find **WhatsApp → Set up**
3. Under **WhatsApp → API Setup**:
   - Copy **Phone Number ID**
   - Copy **WhatsApp Business Account ID**
   - Copy **Temporary Access Token**
4. Add your test phone number → verify with OTP
5. Expose your server with ngrok:

```bash
ngrok http 8000
```

6. Under **WhatsApp → Configuration → Webhook**, set Callback URL to:

```text
https://your-ngrok-url/webhook/whatsapp/your-tenant-slug
```

- Enter your Verify Token
- Subscribe to **messages** webhook field

1. Send a WhatsApp message to your test number

> For production, replace the temporary access token with a permanent System User token from Meta Business Suite.

---

## Webhook URLs Summary

| Channel | Method | URL |
|---|---|---|
| LINE | POST | `/webhook/line/{tenant_slug}` |
| Messenger | POST | `/webhook/messenger/{tenant_slug}` |
| Messenger verify | GET | `/webhook/messenger/{tenant_slug}` |

---

## Admin Endpoints

| Endpoint | Description |
|---|---|
| `GET /admin/conversations?tenant_id=xxx` | List all conversations |
| `GET /admin/conversations/{id}` | View full conversation with messages |
| `GET /admin/stats/{tenant_id}` | Total conversations and messages |

---

## Supported Verticals & Pre-built Prompts

| Vertical | Bot Name | Use Case |
|---|---|---|
| `clinic` | HealthBot | Appointment booking, medical FAQs |
| `real_estate` | PropertyBot | Property listings, viewings |
| `ecommerce` | ShopBot | Order tracking, returns |
| `logistics` | TrackBot | Shipment tracking, delivery |
| `education` | EduBot | Enrollment, course info |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `GROQ_API_KEY` | Groq API key from console.groq.com |
| `APP_ENV` | `development` or `production` |
| `SECRET_KEY` | Random secret for security |

---

## Useful Commands

```bash
# Start services
docker-compose up --build

# Stop services
docker-compose down

# Run migrations
docker-compose exec app alembic revision --autogenerate -m "migration name"
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app

# Restart app only
docker-compose restart app
```
