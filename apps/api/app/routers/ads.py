import secrets
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
from ..db import get_db
from ..dependencies import get_current_user
from ..models import AdEvent
from ..config import settings

router = APIRouter(prefix="/api/ads")


def redis_client():
    return Redis.from_url(settings.redis_url, decode_responses=True)


@router.post("/start")
def ads_start(db: Session = Depends(get_db), user=Depends(get_current_user)):
    event = AdEvent(user_id=user.id, status="started")
    db.add(event)
    db.commit()
    return {"status": "started"}


@router.post("/complete")
def ads_complete(db: Session = Depends(get_db), user=Depends(get_current_user)):
    nonce = secrets.token_urlsafe(16)
    event = AdEvent(user_id=user.id, status="completed", nonce=nonce, completed_at=datetime.utcnow())
    db.add(event)
    db.commit()
    redis = redis_client()
    redis.setex(f"adpass:{user.id}:{nonce}", settings.ad_pass_ttl_seconds, "1")
    return {"nonce": nonce}
