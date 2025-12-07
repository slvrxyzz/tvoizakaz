from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from redis.exceptions import RedisError

from src.config import settings
from src.infrastructure.cache.redis_client import get_redis_client


logger = logging.getLogger(__name__)


@dataclass
class _FallbackToken:
    user_id: int
    expires_at: datetime


class PasswordResetTokenStore:
    def __init__(self, ttl_seconds: int, prefix: str = "auth:reset:"):
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix
        self.redis = get_redis_client()
        self._fallback: Dict[str, _FallbackToken] = {}
        self._lock = asyncio.Lock()

    def _key(self, token: str) -> str:
        return f"{self.prefix}{token}"

    async def set(self, token: str, user_id: int) -> None:
        key = self._key(token)
        try:
            await self.redis.set(key, user_id, ex=self.ttl_seconds)
        except RedisError as exc:
            logger.warning("Password reset token stored in fallback: %s", str(exc))
            expires_at = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
            async with self._lock:
                self._fallback[token] = _FallbackToken(user_id=user_id, expires_at=expires_at)

    async def get_user_id(self, token: str) -> Optional[int]:
        key = self._key(token)
        try:
            value = await self.redis.get(key)
            return int(value) if value is not None else None
        except RedisError as exc:
            logger.warning("Password reset token fallback read: %s", str(exc))
            async with self._lock:
                entry = self._fallback.get(token)
                if not entry:
                    return None
                if entry.expires_at < datetime.utcnow():
                    self._fallback.pop(token, None)
                    return None
                return entry.user_id

    async def delete(self, token: str) -> None:
        key = self._key(token)
        try:
            await self.redis.delete(key)
        except RedisError as exc:
            logger.warning("Password reset token fallback delete: %s", str(exc))
            async with self._lock:
                self._fallback.pop(token, None)

    async def exists(self, token: str) -> bool:
        user_id = await self.get_user_id(token)
        return user_id is not None


reset_token_store = PasswordResetTokenStore(settings.password_reset_token_ttl)

