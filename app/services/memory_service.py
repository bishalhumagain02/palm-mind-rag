import json
import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
TTL_SECONDS = 60 * 60 * 24

def get_history(session_id: str) -> list[dict[str, str]]:
    raw = redis_client.get(f"chat:{session_id}")
    return json.loads(raw) if raw else []

def save_history(session_id: str, history: list[dict[str, str]]) -> None:
    redis_client.setex(f"chat:{session_id}", TTL_SECONDS, json.dumps(history[-20:]))
