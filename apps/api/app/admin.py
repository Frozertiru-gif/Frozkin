from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from starlette.responses import RedirectResponse
from .config import settings
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


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.admin_user and password == settings.admin_pass:
            request.session.update({"token": "admin"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") == "admin"


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.tg_user_id, User.username, User.is_premium]


class TitleAdmin(ModelView, model=Title):
    column_list = [Title.id, Title.type, Title.title, Title.year]


class SeasonAdmin(ModelView, model=Season):
    column_list = [Season.id, Season.series_id, Season.season_number]


class EpisodeAdmin(ModelView, model=Episode):
    column_list = [Episode.id, Episode.season_id, Episode.episode_number]


class MediaVariantAdmin(ModelView, model=MediaVariant):
    column_list = [MediaVariant.id, MediaVariant.scope_type, MediaVariant.status]


class UploadJobAdmin(ModelView, model=UploadJob):
    column_list = [UploadJob.id, UploadJob.media_variant_id, UploadJob.status]


class FavoriteAdmin(ModelView, model=Favorite):
    column_list = [Favorite.id, Favorite.user_id, Favorite.title_id]


class UserPremiumAdmin(ModelView, model=UserPremium):
    column_list = [UserPremium.id, UserPremium.user_id, UserPremium.is_active]


class ReferralCodeAdmin(ModelView, model=ReferralCode):
    column_list = [ReferralCode.id, ReferralCode.owner_user_id, ReferralCode.code]


class ReferralAdmin(ModelView, model=Referral):
    column_list = [Referral.id, Referral.inviter_user_id, Referral.invitee_user_id]
