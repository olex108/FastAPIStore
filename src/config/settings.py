# config/settings.py
import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

debug_logger = logging.getLogger("debug")


class Settings(BaseSettings):
    app_name: str = "fastapistore"
    admin_email: str = "admin@example.com"
    items_per_user: int = 50

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # project
    SECRET_KEY: str
    DEBUG: bool
    HOST: str = "127.0.0.1"
    PORT: int = 8880

    DEBUG_TOOLBAR: bool = True

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # игнорировать лишние переменные в .env
        case_sensitive=False,
        env_nested_delimiter="",
    )

    @property
    def DATABASE_SYNC_URL(self):
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_ASYNC_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# получение переменных из настроек с их сохранением в кеш
@lru_cache()
def get_settings():
    debug_logger.debug("--- Create settings ---")
    return Settings()
