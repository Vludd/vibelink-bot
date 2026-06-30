from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Telegram
    bot_token: str
    admin_ids: list[int] = []

    # Database
    database_url: str  # e.g. postgresql+asyncpg://user:pass@localhost:5432/vibelink
    db_echo: bool = False

    # Redis (FSM storage + throttling middleware)
    redis_url: str = "redis://localhost:6379/0"

    # Throttling
    throttle_rate_limit: float = 0.5  # seconds between messages per user

    # Misc
    log_level: str = "INFO"


settings = Settings() # pyright: ignore[reportCallIssue]