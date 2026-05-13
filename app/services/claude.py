from groq import AsyncGroq

from app.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

MAX_HISTORY_MESSAGES = 20
DEFAULT_MODEL = "llama-3.3-70b-versatile"


async def get_claude_reply(
    system_prompt: str,
    history: list[dict],
    user_message: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    messages += _trim_history(history)
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _trim_history(history: list[dict]) -> list[dict]:
    return history[-MAX_HISTORY_MESSAGES:] if len(history) > MAX_HISTORY_MESSAGES else history


def build_history(messages: list) -> list[dict]:
    return [{"role": msg.role, "content": msg.content} for msg in messages]
