from pydantic import BaseModel
from typing import List, Optional


class TelegramAuthIn(BaseModel):
    initData: str


class AuthResponse(BaseModel):
    access_token: str


class TitleOut(BaseModel):
    id: int
    type: str
    title: str
    description: str
    year: int
    poster_url: Optional[str] = None
    tags: Optional[str] = None


class SeasonOut(BaseModel):
    id: int
    season_number: int
    title: Optional[str] = None


class EpisodeOut(BaseModel):
    id: int
    episode_number: int
    title: str
    description: Optional[str] = None
    duration_sec: Optional[int] = None


class TitleDetailOut(TitleOut):
    seasons: List[SeasonOut] = []
    episodes: List[EpisodeOut] = []


class VariantOut(BaseModel):
    id: int
    audio_code: str
    quality_code: str
    status: str


class WatchRequestIn(BaseModel):
    scope_type: str
    scope_id: int
    audio: str
    quality: str
    ad_nonce: str | None = None


class WatchResponse(BaseModel):
    action: str
    variant_id: Optional[int] = None
    url: Optional[str] = None


class FavoriteOut(BaseModel):
    id: int
    title_id: int


class MeOut(BaseModel):
    is_premium: bool
    premium_until: Optional[str] = None
