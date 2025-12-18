"""Redis-backed JWT blocklist to mitigate replay after logout or suspicion."""
from __future__ import annotations

import datetime as dt

from redis.asyncio import Redis


class TokenBlocklist:
    """Track revoked JWT identifiers until their natural expiration."""

    def __init__(
        self,
        *,
        redis_host: str,
        redis_port: int,
        redis_password: str | None = None,
    ) -> None:
        self._redis = Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )

    async def initialize(self) -> None:
        await self._redis.ping()

    async def close(self) -> None:
        await self._redis.close()

    async def is_blocked(self, jti: str) -> bool:
        return bool(await self._redis.exists(self._key(jti)))

    async def block_until_expiry(self, jti: str, exp_timestamp: int) -> None:
        """Mark a token identifier as revoked until its expiry to prevent replay."""

        now_ts = int(dt.datetime.now(dt.timezone.utc).timestamp())
        ttl_seconds = max(exp_timestamp - now_ts, 0)
        # Ensure the key sticks for at least a second to cover edge race conditions.
        await self._redis.set(self._key(jti), "revoked", ex=max(ttl_seconds, 1))

    @staticmethod
    def _key(jti: str) -> str:
        return f"revoked:{jti}"
