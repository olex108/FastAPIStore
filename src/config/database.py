# database.py
import logging

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from databases import Database
from .settings import get_settings

# Logging
debug_logger = logging.getLogger("debug")

debug_logger.debug("--- Database start ---")


class DatabaseHandler(ABC):
    # @abstractmethod
    # def __init__(
    #     self,
    #     database_url: str,
    #     echo: bool = False,
    #     pool_size: int = 5,
    #     max_overflow: int = 10,
    # ):
    #     self
    pass


class DatabaseSyncHandler(DatabaseHandler):
    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):

        # Движок для синхронного использования
        engine = create_engine(database_url)
        # Создание фабрики сессий
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Async database
class DatabaseAsyncHandler(DatabaseHandler):
    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:

        self.engine: AsyncEngine = create_async_engine(
            url=database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )

        # Движок для асинхронного использования
        # database = Database(DATABASE_URL)

    async def dispose(self) -> None:
        """Асинхронный метод для закрытия сессии"""
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """Зависимость для FastAPI"""

        async with self.session_maker as session:
            try:
                yield session
            finally:
                await session.close()


# Database configuration
settings = get_settings()

db_handler = DatabaseAsyncHandler(
    database_url=str(settings.DATABASE_ASYNC_URL),
    echo=settings.DEBUG,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
)
