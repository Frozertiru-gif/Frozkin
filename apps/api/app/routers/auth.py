import json
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import verify_telegram_init_data, create_access_token
from ..models import User, ReferralCode, Referral
from ..schemas import TelegramAuthIn, AuthResponse

router = APIRouter(prefix="/api/auth")


@router.post("/telegram", response_model=AuthResponse)
def telegram_auth(payload: TelegramAuthIn, db: Session = Depends(get_db)):
    data = verify_telegram_init_data(payload.initData)
    user_data = json.loads(data["user"])
    tg_user_id = int(user_data["id"])
    user = db.query(User).filter(User.tg_user_id == tg_user_id).first()
    if not user:
        user = User(
            tg_user_id=tg_user_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
        )
        db.add(user)
        db.flush()
        code = secrets.token_hex(4)
        db.add(ReferralCode(owner_user_id=user.id, code=code))
    else:
        user.username = user_data.get("username")
        user.first_name = user_data.get("first_name")
        user.last_name = user_data.get("last_name")

    db.commit()
    token = create_access_token(
        {"user_id": user.id, "tg_user_id": user.tg_user_id, "exp": datetime.utcnow() + timedelta(days=7)}
    )
    return AuthResponse(access_token=token)
