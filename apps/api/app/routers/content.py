from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..dependencies import get_current_user
from ..models import Title, TitleType, Season, Episode, MediaVariant, AudioTrack, Quality, VariantScope
from ..schemas import TitleDetailOut, SeasonOut, EpisodeOut, VariantOut

router = APIRouter(prefix="/api")


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


@router.get("/episodes/{episode_id}")
def episode_detail(episode_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    variants = (
        db.query(MediaVariant, AudioTrack, Quality)
        .join(AudioTrack, MediaVariant.audio_track_id == AudioTrack.id)
        .join(Quality, MediaVariant.quality_id == Quality.id)
        .filter(MediaVariant.episode_id == episode_id)
        .all()
    )
    return {
        "episode": {
            "id": episode.id,
            "episode_number": episode.episode_number,
            "title": episode.title,
            "description": episode.description,
            "duration_sec": episode.duration_sec,
        },
        "variants": [
            {
                "id": variant.id,
                "audio_code": audio.code,
                "quality_code": quality.code,
                "status": variant.status,
            }
            for variant, audio, quality in variants
        ],
    }


@router.get("/variants", response_model=list[VariantOut])
def list_variants(
    scope: VariantScope,
    scope_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = (
        db.query(MediaVariant, AudioTrack, Quality)
        .join(AudioTrack, MediaVariant.audio_track_id == AudioTrack.id)
        .join(Quality, MediaVariant.quality_id == Quality.id)
    )
    if scope == VariantScope.movie:
        query = query.filter(MediaVariant.title_id == scope_id)
    else:
        query = query.filter(MediaVariant.episode_id == scope_id)
    variants = query.all()
    return [
        VariantOut(id=v.id, audio_code=a.code, quality_code=q.code, status=v.status)
        for v, a, q in variants
    ]
