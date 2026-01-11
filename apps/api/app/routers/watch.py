from fastapi import APIRouter, Depends, HTTPException
import secrets
import httpx
from sqlalchemy.orm import Session
from redis import Redis
from ..db import get_db
from ..dependencies import get_current_user
from ..models import MediaVariant, AudioTrack, Quality, VariantScope
from ..schemas import WatchRequestIn, WatchResponse
from ..config import settings

router = APIRouter(prefix="/api/watch")


def redis_client():
    return Redis.from_url(settings.redis_url, decode_responses=True)


def cooldown_key(user_id: int, variant_id: int) -> str:
    return f"variant:cooldown:{user_id}:{variant_id}"


def create_delivery_token(redis: Redis, user_id: int, variant_id: int) -> str:
    token = secrets.token_urlsafe(16)
    redis.setex(
        f"delivery:{token}",
        settings.delivery_token_ttl_seconds,
        f"{user_id}:{variant_id}",
    )
    redis.setex(cooldown_key(user_id, variant_id), settings.variant_cooldown_seconds, "1")
    return token


@router.post("/request", response_model=WatchResponse)
def watch_request(payload: WatchRequestIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    variant_query = (
        db.query(MediaVariant, AudioTrack, Quality)
        .join(AudioTrack, MediaVariant.audio_track_id == AudioTrack.id)
        .join(Quality, MediaVariant.quality_id == Quality.id)
    )
    if payload.scope_type == VariantScope.movie:
        variant_query = variant_query.filter(MediaVariant.title_id == payload.scope_id)
    else:
        variant_query = variant_query.filter(MediaVariant.episode_id == payload.scope_id)
    variant = (
        variant_query.filter(AudioTrack.code == payload.audio)
        .filter(Quality.code == payload.quality)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    media_variant = variant[0]

    redis = redis_client()
    if redis.get(cooldown_key(user.id, media_variant.id)):
        raise HTTPException(status_code=429, detail="Variant cooldown active")

    if user.is_premium:
        token = create_delivery_token(redis, user.id, media_variant.id)
        return WatchResponse(action="deliver", delivery_token=token)

    if payload.ad_nonce:
        key = f"adpass:{user.id}:{payload.ad_nonce}"
        if redis.get(key):
            redis.delete(key)
            token = create_delivery_token(redis, user.id, media_variant.id)
            return WatchResponse(action="deliver", delivery_token=token)

    return WatchResponse(action="ad_gate", url="/ad-gate")


@router.post("/deliver")
def deliver_video(delivery_token: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    redis = redis_client()
    token_key = f"delivery:{delivery_token}"
    token_value = redis.execute_command("GETDEL", token_key)
    if not token_value:
        raise HTTPException(status_code=403, detail="Invalid delivery token")
    token_user_id, token_variant_id = token_value.split(":", maxsplit=1)
    if int(token_user_id) != user.id:
        raise HTTPException(status_code=403, detail="Invalid delivery token")

    variant = db.query(MediaVariant).filter(MediaVariant.id == int(token_variant_id)).first()
    if not variant or not variant.telegram_file_id:
        raise HTTPException(status_code=409, detail="Variant not ready")
    payload = {"chat_id": user.tg_user_id, "file_id": variant.telegram_file_id}
    with httpx.Client() as client:
        response = client.post(f"{settings.bot_service_url}/deliver", json=payload, timeout=10)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Bot delivery failed")
    return {"status": "queued"}
