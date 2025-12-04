"""Asynchronous Redis-backed rate limiter to throttle abusive clients."""
from __future__ import annotations

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis


class RateLimiter:
    """Simple fixed-window limiter counting requests per IP + route."""

    def __init__(self, *, redis_host: str, redis_port: int, limit: int = 20, window_seconds: int = 60) -> None:
        self._redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.limit = limit
        self.window_seconds = window_seconds

    async def initialize(self) -> None:
        # Connectivity test ensures misconfiguration is caught early.
        await self._redis.ping()

    async def close(self) -> None:
        await self._redis.close()

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}:{request.url.path}"
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
