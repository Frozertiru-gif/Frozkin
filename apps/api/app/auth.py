import hashlib
import hmac
import time
from urllib.parse import parse_qsl
import jwt
from fastapi import HTTPException
from .config import settings


def verify_telegram_init_data(init_data: str) -> dict:
    data = dict(parse_qsl(init_data, keep_blank_values=True))
    if "hash" not in data:
        raise HTTPException(status_code=400, detail="Invalid init data")

    received_hash = data.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="Invalid signature")

    auth_date = int(data.get("auth_date", "0"))
    if int(time.time()) - auth_date > 86400:
        raise HTTPException(status_code=401, detail="Init data expired")

    user = data.get("user")
    if not user:
        raise HTTPException(status_code=400, detail="User missing")
    return data


def create_access_token(payload: dict) -> str:
    return jwt.encode(payload, settings.api_secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.api_secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
