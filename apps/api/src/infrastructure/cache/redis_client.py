from __future__ import annotations

import json
from typing import Any

import structlog
import redis.asyncio as aioredis

log = structlog.get_logger()

_redis: aioredis.Redis | None = None


class RedisClient:
    @classmethod
    async def initialize(cls, url: str) -> None:
        global _redis
        _redis = aioredis.from_url(url, encoding="utf-8", decode_responses=True)
        await _redis.ping()
        log.info("redis_connected")

    @classmethod
    async def close(cls) -> None:
        global _redis
        if _redis:
            await _redis.aclose()

    @classmethod
    def get(cls) -> aioredis.Redis:
        if _redis is None:
            raise RuntimeError("Redis not initialized. Call RedisClient.initialize() first.")
        return _redis


async def cache_get(key: str) -> Any | None:
    try:
        value = await RedisClient.get().get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception as e:
        log.warning("cache_get_failed", key=key, error=str(e))
        return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    try:
        await RedisClient.get().setex(key, ttl, json.dumps(value))
    except Exception as e:
        log.warning("cache_set_failed", key=key, error=str(e))


async def cache_delete(key: str) -> None:
    try:
        await RedisClient.get().delete(key)
    except Exception as e:
        log.warning("cache_delete_failed", key=key, error=str(e))


async def rate_limit_check(key: str, max_requests: int, window_seconds: int = 60) -> bool:
    """Returns True if request is allowed, False if rate limit exceeded."""
    try:
        client = RedisClient.get()
        current = await client.incr(key)
        if current == 1:
            await client.expire(key, window_seconds)
        return current <= max_requests
    except Exception:
        return True  # Fail open on Redis errors
