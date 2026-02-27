import redis.asyncio as redis

from src.core.config import redis_config

redis_client = redis.from_url(
    redis_config.redis_url,
    decode_responses=True,
)
