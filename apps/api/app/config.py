from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    bot_token: str = ""
    api_secret_key: str = ""
    env: str = "dev"
    enable_docs: bool = True
    admin_user: str = "admin"
    admin_pass: str = "change_me"
    public_base_url: str = ""
    webapp_public_url: str = ""
    api_public_url: str = ""
    bot_service_url: str = "http://bot:8085"
    ad_pass_ttl_seconds: int = 600
    delivery_token_ttl_seconds: int = 600
    variant_cooldown_seconds: int = 600
    rate_limits_json: str = ""

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


settings = Settings()
