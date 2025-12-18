"""Redis-backed rate limiter keyed by client IP to stop brute force."""
from __future__ import annotations

from typing import Iterable

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from .security import extract_client_ip


class RateLimiter:
    """Fixed-window rate limiter with per-endpoint namespaces."""

    def __init__(
        self,
        *,
        redis_host: str,
        redis_port: int,
        redis_password: str | None,
        limit: int,
        window_seconds: int,
        key_prefix: str,
    ) -> None:
        self._redis = Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )
        self.limit = limit
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix

    async def initialize(self) -> None:
        await self._redis.ping()

    async def close(self) -> None:
        await self._redis.close()

    async def __call__(self, request: Request) -> None:
        client_ip = extract_client_ip(request)
        key = f"{self.key_prefix}:{client_ip}"
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, self.window_seconds)
        if current > self.limit:
            reset = await self._redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(max(reset, 0))},
            )


def warmup_rate_limiters(limiters: Iterable[RateLimiter]) -> list[RateLimiter]:
    """Utility to hydrate multiple rate limiters during startup."""

    return list(limiters)
