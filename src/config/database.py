# database.py
import logging
from abc import ABC, abstractmethod
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from .settings import get_settings

# Logging
debug_logger = logging.getLogger("debug")
# Database configuration
settings = get_settings()


class DatabaseHandler(ABC):
    """Абстрактный класс для работы с базой данных"""

    def __init__(self):
        self.engine = None
        self.session_maker = None

    @abstractmethod
    def init_db(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """Метод для инициализации движка и фабрики сессий"""
        pass


class DatabaseSyncHandler(DatabaseHandler):
    """Класс для синхронной работы с базой данных"""

    def init_db(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """Метод для инициализации движка и фабрики сессий"""

        # Движок для синхронного использования
        self.engine = create_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        # Создание фабрики сессий
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)


class DatabaseAsyncHandler(DatabaseHandler):
    """Класс для асинхронной работы с базой данных"""

    def init_db(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """Метод для инициализации движка и фабрики сессий"""

        debug_logger.debug("--- Database handler init ---")
        self.engine: AsyncEngine = create_async_engine(
            url=database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False, expire_on_commit=False
        )


    async def dispose(self) -> None:
        """Асинхронный метод для закрытия сессии"""

        debug_logger.debug("--- Database handler dispose ---")
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """Зависимость для FastAPI"""

        debug_logger.debug("--- Database handler session_maker get ---")
        async with self.session_maker() as session:
            yield session


db_handler = DatabaseAsyncHandler()
