from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..dependencies import get_current_user
from ..models import UserPremium, PremiumPlan
from ..schemas import MeOut

router = APIRouter(prefix="/api")


@router.get("/me", response_model=MeOut)
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    premium = (
        db.query(UserPremium)
        .filter(UserPremium.user_id == user.id, UserPremium.is_active == True)
        .first()
    )
    premium_until = premium.ends_at.isoformat() if premium else None
    return MeOut(is_premium=user.is_premium or bool(premium), premium_until=premium_until)


@router.post("/premium/activate-dev")
def activate_premium(user=Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(PremiumPlan).first()
    if not plan:
        plan = PremiumPlan(name="Monthly", price=499, duration_days=30)
        db.add(plan)
        db.flush()
    premium = UserPremium(
        user_id=user.id,
        plan_id=plan.id,
        starts_at=datetime.utcnow(),
        ends_at=datetime.utcnow() + timedelta(days=plan.duration_days),
        is_active=True,
    )
    user.is_premium = True
    db.add(premium)
    db.commit()
    return {"status": "activated"}
