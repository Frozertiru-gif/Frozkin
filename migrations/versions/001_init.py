"""init

Revision ID: 001
Revises: 
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(length=255)),
        sa.Column("first_name", sa.String(length=255)),
        sa.Column("last_name", sa.String(length=255)),
        sa.Column("is_premium", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "titles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.Enum("movie", "series", name="titletype"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("poster_url", sa.String(length=500)),
        sa.Column("tags", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("series_id", sa.Integer(), sa.ForeignKey("titles.id"), nullable=False),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255)),
    )
    op.create_table(
        "episodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("duration_sec", sa.Integer()),
    )
    op.create_table(
        "audio_tracks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_table(
        "qualities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_table(
        "media_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope_type", sa.Enum("movie", "episode", name="variantscope"), nullable=False),
        sa.Column("title_id", sa.Integer(), sa.ForeignKey("titles.id")),
        sa.Column("episode_id", sa.Integer(), sa.ForeignKey("episodes.id")),
        sa.Column("audio_track_id", sa.Integer(), sa.ForeignKey("audio_tracks.id"), nullable=False),
        sa.Column("quality_id", sa.Integer(), sa.ForeignKey("qualities.id"), nullable=False),
        sa.Column("telegram_file_id", sa.String(length=255)),
        sa.Column("file_size_mb", sa.Integer()),
        sa.Column("source_path", sa.String(length=500)),
        sa.Column("status", sa.Enum("pending", "uploaded", "failed", name="variantstatus")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("scope_type", "title_id", "episode_id", "audio_track_id", "quality_id"),
    )
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title_id", sa.Integer(), sa.ForeignKey("titles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "title_id"),
    )
    op.create_table(
        "view_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("media_variant_id", sa.Integer(), sa.ForeignKey("media_variants.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("meta", sa.JSON()),
    )
    op.create_table(
        "upload_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_variant_id", sa.Integer(), sa.ForeignKey("media_variants.id"), nullable=False),
        sa.Column("status", sa.Enum("pending", "running", "done", "failed", name="uploadstatus")),
        sa.Column("last_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "ad_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("nonce", sa.String(length=255)),
        sa.Column("status", sa.String(length=50), nullable=False),
    )
    op.create_table(
        "premium_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "user_premium",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("premium_plans.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("premium_plans.id"), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "referral_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inviter_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("invitee_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "referral_rewards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("referral_rewards")
    op.drop_table("referrals")
    op.drop_table("referral_codes")
    op.drop_table("payments")
    op.drop_table("user_premium")
    op.drop_table("premium_plans")
    op.drop_table("ad_events")
    op.drop_table("upload_jobs")
    op.drop_table("view_events")
    op.drop_table("favorites")
    op.drop_table("media_variants")
    op.drop_table("qualities")
    op.drop_table("audio_tracks")
    op.drop_table("episodes")
    op.drop_table("seasons")
    op.drop_table("titles")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS titletype")
    op.execute("DROP TYPE IF EXISTS variantscope")
    op.execute("DROP TYPE IF EXISTS variantstatus")
    op.execute("DROP TYPE IF EXISTS uploadstatus")
