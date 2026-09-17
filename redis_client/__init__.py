from typing import Optional
from core.config import settings

# Try to import async redis implementations, but don't fail at import time.
# If neither is available, `aioredis_impl` remains None and we raise a clear
# error when code actually attempts to create a client.
aioredis_impl = None
try:
    import redis.asyncio as _redis_asyncio  # type: ignore
    aioredis_impl = _redis_asyncio
except Exception:
    try:
        import aioredis as _aioredis  # type: ignore
        aioredis_impl = _aioredis
    except Exception:
        aioredis_impl = None

client: Optional[object] = None

async def create_redis_client() -> object:
    global client
    if aioredis_impl is None:
        raise RuntimeError(
            "Async Redis library not found. Install 'redis>=4' (`pip install redis>=4.6`) or 'aioredis'."
        )
    if client is None:
        # redis-py >=4 exposes `from_url` on redis.asyncio
        client = aioredis_impl.from_url(settings.REDIS_URL, decode_responses=True)
    return client

async def close_redis() -> None:
    global client
    if client is not None:
        try:
            await client.close()
        except Exception:
            try:
                await client.disconnect()
            except Exception:
                pass
        client = None

async def cache_set(key: str, value: str, expire_seconds: int = 300) -> None:
    redis_client = await create_redis_client()
    await redis_client.set(key, value, ex=expire_seconds)

async def cache_get(key: str) -> Optional[str]:
    redis_client = await create_redis_client()
    return await redis_client.get(key)
