from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from .auth import decode_access_token
from .models import User
from .db import get_db


def get_current_user(
    request: Request,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    request.state.tg_user_id = user.tg_user_id
    return user
