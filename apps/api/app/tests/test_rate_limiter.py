import pytest
from fastapi import Request, HTTPException
from app.rate_limiter import RateLimiter


class DummyRedis:
    def __init__(self):
        self.calls = 0

    def incr(self, key):
        self.calls += 1
        return 100

    def expire(self, key, ttl):
        return True


class DummyRequest(Request):
    def __init__(self, scope):
        super().__init__(scope)


@pytest.mark.asyncio
async def test_rate_limit_exceeded(monkeypatch):
    limiter = RateLimiter()
    limiter.redis = DummyRedis()
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/catalog/search",
        "headers": [],
        "scheme": "http",
        "server": ("test", 80),
        "client": ("127.0.0.1", 1234),
        "root_path": "",
        "query_string": b"",
    }
    request = DummyRequest(scope)
    with pytest.raises(HTTPException):
        await limiter.check(request, "user")
