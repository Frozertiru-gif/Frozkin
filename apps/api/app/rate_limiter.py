import json
import time
from fastapi import Request, HTTPException
from redis import Redis
from .config import settings

DEFAULT_LIMITS = {
    "/api/catalog/search": {"limit": 30, "window": 60},
    "/api/catalog/top": {"limit": 60, "window": 60},
    "/api/watch/request": {"limit": 10, "window": 60},
    "/api/ads": {"limit": 20, "window": 60},
    "/api/auth/telegram": {"limit": 10, "window": 60},
}


def load_limits():
    if settings.rate_limits_json:
        return json.loads(settings.rate_limits_json)
    return DEFAULT_LIMITS


class RateLimiter:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self.limits = load_limits()

    def _key(self, request: Request, identifier: str) -> str:
        return f"rl:{identifier}:{request.url.path}"

    async def check(self, request: Request, identifier: str):
        path = request.url.path
        config = None
        for key, value in self.limits.items():
            if path.startswith(key):
                config = value
                break
        if not config:
            return
        limit = int(config["limit"])
        window = int(config["window"])
        key = self._key(request, identifier)
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        if current > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
