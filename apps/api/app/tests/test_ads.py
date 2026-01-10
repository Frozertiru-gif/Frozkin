from app.routers import ads


class DummyRedis:
    def __init__(self):
        self.key = None
        self.ttl = None

    def setex(self, key, ttl, value):
        self.key = key
        self.ttl = ttl
        return True


def test_ads_complete_sets_nonce(monkeypatch):
    redis = DummyRedis()

    def fake_redis():
        return redis

    monkeypatch.setattr(ads, "redis_client", fake_redis)

    class DummyUser:
        id = 1

    class DummyDB:
        def add(self, item):
            return None

        def commit(self):
            return None

    response = ads.ads_complete(user=DummyUser(), db=DummyDB())
    assert "nonce" in response
    assert redis.key.startswith("adpass:1:")
