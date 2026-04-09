# database.py
import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from databases import Database
from .settings import get_settings

# Logging
debug_logger = logging.getLogger("debug")

debug_logger.debug("--- Database start ---")

# Database configuration
settings = get_settings()
DATABASE_ASYNC_URL = get_settings().DATABASE_ASYNC_URL

# Sync database
# Движок для синхронного использования
# engine = create_engine(DATABASE_SYNC_URL)

# metadata = MetaData()

# Движок для асинхронного использования
# database = Database(DATABASE_URL)

# Создание фабрики сессий
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async database
async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
    # pool_size=10,
    # max_overflow=10,
)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
