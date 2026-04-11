# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "fastapistore"
    admin_email: str = "admin@example.com"
    items_per_user: int = 50

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    SECRET_KEY: str
    DEBUG: bool

    # Database
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 50

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding='utf-8',
        extra='ignore'  # игнорировать лишние переменные в .env
    )

    @property
    def DATABASE_SYNC_URL(self):
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    @property
    def DATABASE_ASYNC_URL(self):
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# получение переменных из настроек с их сохранением в кеш
@lru_cache()
def get_settings():
    return Settings()
