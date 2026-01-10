import hashlib
import hmac
import json
from urllib.parse import urlencode
from app.auth import verify_telegram_init_data
from app.config import settings


def make_init_data(user_id: int):
    user = json.dumps({"id": user_id, "first_name": "Test"})
    data = {"auth_date": "1700000000", "user": user}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.bot_token.encode()).digest()
    data_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    data["hash"] = data_hash
    return urlencode(data)


def test_verify_telegram_init_data(monkeypatch):
    monkeypatch.setattr(settings, "bot_token", "test-token")
    init_data = make_init_data(123)
    parsed = verify_telegram_init_data(init_data)
    assert "user" in parsed
