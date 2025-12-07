import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.monitoring.logger import logger as app_logger


class RateLimiter:
    def __init__(self, requests_per_window: int = 60, window_size: int = 60):
        self.requests_per_window = requests_per_window
        self.window_size = window_size
        self._fallback_notice_sent = False
        try:
            self.redis = get_redis_client()
        except RedisError as exc:
            app_logger.warning("Redis unavailable for rate limiter", error=str(exc))
            self.redis = None
            self._fallback_notice_sent = True
        self._fallback_requests: Dict[str, deque] = defaultdict(deque)
        self._fallback_lock = asyncio.Lock()

    def _key(self, endpoint: str, client_ip: str) -> str:
        return f"rate-limit:{endpoint}:{client_ip}"

    async def check(self, client_ip: str, endpoint: str = "global") -> Tuple[bool, int, int]:
        key = self._key(endpoint, client_ip)
        if self.redis is None:
            if not self._fallback_notice_sent:
                app_logger.warning("Rate limiter using in-memory fallback", endpoint=endpoint)
                self._fallback_notice_sent = True
            return await self._check_fallback(key)

        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, self.window_size)
                ttl = self.window_size
            else:
                ttl = await self.redis.ttl(key)
                if ttl in (-1, -2):
                    await self.redis.expire(key, self.window_size)
                    ttl = self.window_size
            allowed = count <= self.requests_per_window
            remaining = max(0, self.requests_per_window - count)
            return allowed, remaining, max(ttl, 0)
        except RedisError as exc:
            app_logger.warning("Rate limiter fallback engaged", error=str(exc))
            return await self._check_fallback(key)

    async def _check_fallback(self, key: str) -> Tuple[bool, int, int]:
        current_time = time.time()
        async with self._fallback_lock:
            queue = self._fallback_requests[key]
            while queue and queue[0] <= current_time - self.window_size:
                queue.popleft()

            if len(queue) >= self.requests_per_window:
                reset_in = int(self.window_size - (current_time - queue[0])) if queue else self.window_size
                return False, 0, max(reset_in, 0)

            queue.append(current_time)
            remaining = self.requests_per_window - len(queue)
            return True, max(remaining, 0), self.window_size


class RateLimitMiddleware:
    def __init__(self, requests_per_window: int = 60, window_seconds: int = 60):
        self.rate_limiter = RateLimiter(requests_per_window, window_seconds)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        allowed, remaining, reset_in = await self.rate_limiter.check(client_ip, request.url.path)

        reset_epoch = int(time.time() + reset_in)

        if not allowed:
            headers = {
                "Retry-After": str(reset_in),
                "X-RateLimit-Limit": str(self.requests_per_window),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_epoch),
            }
            app_logger.performance("rate_limit_exceeded", duration=0, ip_address=client_ip, endpoint=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers=headers,
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_epoch)

        return response
