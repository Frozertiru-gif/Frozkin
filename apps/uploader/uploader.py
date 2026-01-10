import os
import time
import httpx
from redis import Redis
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
import enum

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STORAGE_CHAT_ID = os.getenv("STORAGE_CHAT_ID", "")
TG_BOT_API_BASE_URL = os.getenv("TG_BOT_API_BASE_URL") or "https://api.telegram.org"
LOCAL_BOT_API_BASE_URL = os.getenv("LOCAL_BOT_API_BASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "app")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

Base = declarative_base()


class VariantStatus(str, enum.Enum):
    pending = "pending"
    uploaded = "uploaded"
    failed = "failed"


class MediaVariant(Base):
    __tablename__ = "media_variants"

    id = Column(Integer, primary_key=True)
    telegram_file_id = Column(String)
    source_path = Column(String)
    status = Column(Enum(VariantStatus))


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
redis = Redis.from_url(REDIS_URL, decode_responses=True)


def api_base_url():
    return LOCAL_BOT_API_BASE_URL or TG_BOT_API_BASE_URL


def upload_variant(variant: MediaVariant) -> bool:
    if not variant.source_path or not os.path.exists(variant.source_path):
        return False
    url = f"{api_base_url()}/bot{BOT_TOKEN}/sendVideo"
    with open(variant.source_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": STORAGE_CHAT_ID}
        response = httpx.post(url, data=data, files=files, timeout=300)
    if response.status_code >= 400:
        return False
    payload = response.json()
    if not payload.get("ok"):
        return False
    file_id = payload["result"]["video"]["file_id"]
    variant.telegram_file_id = file_id
    variant.status = VariantStatus.uploaded
    return True


def main():
    while True:
        with Session(engine) as db:
            variants = db.execute(
                select(MediaVariant).where(MediaVariant.status == VariantStatus.pending).limit(2)
            ).scalars().all()
            for variant in variants:
                lock_key = f"upload_lock:{variant.id}"
                if not redis.set(lock_key, "1", nx=True, ex=60):
                    continue
                success = upload_variant(variant)
                if not success:
                    variant.status = VariantStatus.failed
                db.add(variant)
                db.commit()
                redis.delete(lock_key)
        time.sleep(10)


if __name__ == "__main__":
    main()
