import redis.asyncio as redis

from src.core.config import redis_config

redis_client = redis.from_url(
    redis_config.redis_url,
    decode_responses=True,
)


async def create_redis_client() -> redis.Redis:
    return await redis.from_url(
        redis_config.redis_url,
        decode_responses=True,
    )
