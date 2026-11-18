from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.core.settings.settings import settings

redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connection=50,
    decode_responses=False,
    health_check_interval=30,
    socker_timeout=5.0,
    socker_connection_timeout=5.0,
)

redis_client = Redis(connection_pool=redis_pool)


async def get_redis() -> AsyncGenerator[Redis, None]:
    yield redis_client
