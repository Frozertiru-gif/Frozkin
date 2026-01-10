import random
from sqlalchemy.orm import Session
from ..models import (
    Title,
    TitleType,
    Season,
    Episode,
    AudioTrack,
    Quality,
    MediaVariant,
    VariantScope,
    VariantStatus,
    PremiumPlan,
)

MOVIE_COUNT = 20
SERIES_COUNT = 10


def seed_data(db: Session):
    if db.query(Title).count() > 0:
        return

    audio_tracks = [
        AudioTrack(code="ru", name="Русский"),
        AudioTrack(code="en", name="English"),
    ]
    qualities = [
        Quality(code="720p", name="HD"),
        Quality(code="1080p", name="Full HD"),
    ]
    db.add_all(audio_tracks + qualities)
    db.flush()

    movies = []
    for i in range(1, MOVIE_COUNT + 1):
        movies.append(
            Title(
                type=TitleType.movie,
                title=f"Movie {i}",
                description="Seed movie description",
                year=2000 + (i % 20),
                poster_url="https://placehold.co/300x450",
                tags="action,seed",
            )
        )
    db.add_all(movies)
    db.flush()

    series = []
    for i in range(1, SERIES_COUNT + 1):
        series.append(
            Title(
                type=TitleType.series,
                title=f"Series {i}",
                description="Seed series description",
                year=2010 + (i % 10),
                poster_url="https://placehold.co/300x450",
                tags="drama,seed",
            )
        )
    db.add_all(series)
    db.flush()

    for title in series:
        for season_number in range(1, 3):
            season = Season(series_id=title.id, season_number=season_number, title=None)
            db.add(season)
            db.flush()
            for episode_number in range(1, 4):
                episode = Episode(
                    season_id=season.id,
                    episode_number=episode_number,
                    title=f"Episode {episode_number}",
                    description="Seed episode",
                    duration_sec=1200,
                )
                db.add(episode)
                db.flush()
                for audio in audio_tracks:
                    for quality in qualities:
                        db.add(
                            MediaVariant(
                                scope_type=VariantScope.episode,
                                episode_id=episode.id,
                                audio_track_id=audio.id,
                                quality_id=quality.id,
                                status=VariantStatus.pending,
                                source_path=f"/data/videos/series_{title.id}_s{season_number}_e{episode_number}.mp4",
                            )
                        )

    for movie in movies:
        for audio in audio_tracks:
            for quality in qualities:
                db.add(
                    MediaVariant(
                        scope_type=VariantScope.movie,
                        title_id=movie.id,
                        audio_track_id=audio.id,
                        quality_id=quality.id,
                        status=VariantStatus.pending,
                        source_path=f"/data/videos/movie_{movie.id}.mp4",
                    )
                )

    db.add(PremiumPlan(name="Monthly", price=499, duration_days=30))
    db.commit()
