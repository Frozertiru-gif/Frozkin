from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..dependencies import get_current_user
from ..models import Favorite
from ..schemas import FavoriteOut

router = APIRouter(prefix="/api/favorites")


@router.post("/{title_id}")
def toggle_favorite(title_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.title_id == title_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False}
    favorite = Favorite(user_id=user.id, title_id=title_id)
    db.add(favorite)
    db.commit()
    return {"favorited": True}


@router.get("", response_model=list[FavoriteOut])
def list_favorites(db: Session = Depends(get_db), user=Depends(get_current_user)):
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    return [FavoriteOut(id=f.id, title_id=f.title_id) for f in favorites]
