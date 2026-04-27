# config/settings.py
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.pagination import PaginationSettings


class BaseAppParams(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class RedisSettings(BaseAppParams):

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


class SMTPSettings(BaseAppParams):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str


class Settings(BaseAppParams):
    app_name: str = "fastapistore"
    admin_email: str = "admin@example.com"
    items_per_user: int = 50

    # Project
    SECRET_KEY: str
    DEBUG: bool
    HOST: str = "127.0.0.1"
    PORT: int = 8888

    # DEBUG_TOOLBAR: bool = True

    # Database
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 50

    # AUTHENTICATION
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    @property
    def DATABASE_SYNC_URL(self):
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_ASYNC_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Imported settings
    REDIS_SETTINGS: RedisSettings = RedisSettings()
    SMTP: SMTPSettings = SMTPSettings()
    pagination: PaginationSettings = PaginationSettings()


# получение переменных из настроек с их сохранением в кеш
@lru_cache()
def get_settings():
    return Settings()
