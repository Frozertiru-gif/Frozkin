from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..dependencies import get_current_user
from ..models import Title, TitleType, Season, Episode
from ..schemas import TitleOut, TitleDetailOut, SeasonOut, EpisodeOut

router = APIRouter(prefix="/api/catalog")


@router.get("/top", response_model=list[TitleOut])
def top_titles(
    type: TitleType = Query(TitleType.movie),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items = db.query(Title).filter(Title.type == type).limit(limit).all()
    return [
        TitleOut(
            id=item.id,
            type=item.type,
            title=item.title,
            description=item.description,
            year=item.year,
            poster_url=item.poster_url,
            tags=item.tags,
        )
        for item in items
    ]


@router.get("/search", response_model=list[TitleOut])
def search_titles(
    q: str,
    type: TitleType = Query(TitleType.movie),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    items = (
        db.query(Title)
        .filter(Title.type == type)
        .filter(Title.title.ilike(f"%{q}%"))
        .limit(50)
        .all()
    )
    return [
        TitleOut(
            id=item.id,
            type=item.type,
            title=item.title,
            description=item.description,
            year=item.year,
            poster_url=item.poster_url,
            tags=item.tags,
        )
        for item in items
    ]


@router.get("/titles/{title_id}", response_model=TitleDetailOut)
def title_detail(title_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    title = db.query(Title).filter(Title.id == title_id).first()
    seasons = []
    episodes = []
    if title and title.type == TitleType.series:
        seasons = db.query(Season).filter(Season.series_id == title.id).all()
        season_ids = [s.id for s in seasons]
        if season_ids:
            episodes = db.query(Episode).filter(Episode.season_id.in_(season_ids)).all()

    return TitleDetailOut(
        id=title.id,
        type=title.type,
        title=title.title,
        description=title.description,
        year=title.year,
        poster_url=title.poster_url,
        tags=title.tags,
        seasons=[SeasonOut(id=s.id, season_number=s.season_number, title=s.title) for s in seasons],
        episodes=[
            EpisodeOut(
                id=e.id,
                episode_number=e.episode_number,
                title=e.title,
                description=e.description,
                duration_sec=e.duration_sec,
            )
            for e in episodes
        ],
    )
