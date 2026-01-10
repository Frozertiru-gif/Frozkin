import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .db import engine, SessionLocal
from .models import (
    User,
    Title,
    Season,
    Episode,
    MediaVariant,
    UploadJob,
    Favorite,
    UserPremium,
    ReferralCode,
    Referral,
)
from .rate_limiter import RateLimiter
from .services.seed import seed_data
from .routers import auth, catalog, content, favorites, ads, watch, me
from .admin import (
    AdminAuth,
    UserAdmin,
    TitleAdmin,
    SeasonAdmin,
    EpisodeAdmin,
    MediaVariantAdmin,
    UploadJobAdmin,
    FavoriteAdmin,
    UserPremiumAdmin,
    ReferralCodeAdmin,
    ReferralAdmin,
)

app = FastAPI(
    docs_url="/api/docs" if settings.enable_docs else None,
    redoc_url="/api/redoc" if settings.enable_docs else None,
    openapi_url="/api/openapi.json" if settings.enable_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.api_secret_key)

rate_limiter = RateLimiter()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    request.state.tg_user_id = None
    identifier = request.headers.get("authorization", "") or request.client.host
    try:
        await rate_limiter.check(request, identifier)
        response = await call_next(request)
    except Exception as exc:
        response = None
        raise exc
    finally:
        latency = int((time.time() - start) * 1000)
        log = {
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code if response else 500,
            "tg_user_id": request.state.tg_user_id,
            "latency_ms": latency,
        }
        print(json.dumps(log))
    return response


@app.on_event("startup")
def on_startup():
    db: Session = SessionLocal()
    try:
        if settings.env == "dev":
            seed_data(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/version")
def version():
    return {"env": settings.env}


app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(content.router)
app.include_router(favorites.router)
app.include_router(ads.router)
app.include_router(watch.router)
app.include_router(me.router)

admin = Admin(app, engine, authentication_backend=AdminAuth())
admin.add_view(UserAdmin)
admin.add_view(TitleAdmin)
admin.add_view(SeasonAdmin)
admin.add_view(EpisodeAdmin)
admin.add_view(MediaVariantAdmin)
admin.add_view(UploadJobAdmin)
admin.add_view(FavoriteAdmin)
admin.add_view(UserPremiumAdmin)
admin.add_view(ReferralCodeAdmin)
admin.add_view(ReferralAdmin)
