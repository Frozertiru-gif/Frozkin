import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    BigInteger,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.sql import func
from .db import Base


class TitleType(str, enum.Enum):
    movie = "movie"
    series = "series"


class VariantScope(str, enum.Enum):
    movie = "movie"
    episode = "episode"


class VariantStatus(str, enum.Enum):
    pending = "pending"
    uploaded = "uploaded"
    failed = "failed"


class UploadStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(TitleType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    poster_url = Column(String(500))
    tags = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey("titles.id"), nullable=False)
    season_number = Column(Integer, nullable=False)
    title = Column(String(255))


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_sec = Column(Integer)


class AudioTrack(Base):
    __tablename__ = "audio_tracks"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)


class Quality(Base):
    __tablename__ = "qualities"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)


class MediaVariant(Base):
    __tablename__ = "media_variants"
    __table_args__ = (
        UniqueConstraint("scope_type", "title_id", "episode_id", "audio_track_id", "quality_id"),
    )

    id = Column(Integer, primary_key=True)
    scope_type = Column(Enum(VariantScope), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.id"))
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    audio_track_id = Column(Integer, ForeignKey("audio_tracks.id"), nullable=False)
    quality_id = Column(Integer, ForeignKey("qualities.id"), nullable=False)
    telegram_file_id = Column(String(255))
    file_size_mb = Column(Integer)
    source_path = Column(String(500))
    status = Column(Enum(VariantStatus), default=VariantStatus.pending)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "title_id"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title_id = Column(Integer, ForeignKey("titles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ViewEvent(Base):
    __tablename__ = "view_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    media_variant_id = Column(Integer, ForeignKey("media_variants.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    meta = Column(JSON)


class UploadJob(Base):
    __tablename__ = "upload_jobs"

    id = Column(Integer, primary_key=True)
    media_variant_id = Column(Integer, ForeignKey("media_variants.id"), nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.pending)
    last_error = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AdEvent(Base):
    __tablename__ = "ad_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    nonce = Column(String(255))
    status = Column(String(50), nullable=False)


class PremiumPlan(Base):
    __tablename__ = "premium_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)


class UserPremium(Base):
    __tablename__ = "user_premium"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("premium_plans.id"), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("premium_plans.id"), nullable=False)
    provider = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    inviter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    amount = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
