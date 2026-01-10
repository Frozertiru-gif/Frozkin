from fastapi import APIRouter, Depends, HTTPException
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

    if user.is_premium:
        return WatchResponse(action="deliver", variant_id=media_variant.id)

    if payload.ad_nonce:
        redis = redis_client()
        key = f"adpass:{user.id}:{payload.ad_nonce}"
        if redis.get(key):
            redis.delete(key)
            return WatchResponse(action="deliver", variant_id=media_variant.id)

    return WatchResponse(action="ad_gate", url="/ad-gate")


@router.post("/deliver")
def deliver_video(variant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    variant = db.query(MediaVariant).filter(MediaVariant.id == variant_id).first()
    if not variant or not variant.telegram_file_id:
        raise HTTPException(status_code=409, detail="Variant not ready")
    payload = {"chat_id": user.tg_user_id, "file_id": variant.telegram_file_id}
    with httpx.Client() as client:
        response = client.post(f"{settings.bot_service_url}/deliver", json=payload, timeout=10)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Bot delivery failed")
    return {"status": "queued"}
