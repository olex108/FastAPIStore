import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient
from src.config.database import db_handler

from src.main import main_app
from src.config.database import DatabaseAsyncHandler  # Импортируйте ваши зависимости
from src.models.base import Base

import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import main_app
from src.config import database as db_module
from alembic import command
from alembic.config import Config
import os

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # Настроить Alembic для тестовой базы
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")

@pytest.fixture(scope="session")
def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    print()
    yield engine
    asyncio.get_event_loop().run_until_complete(engine.dispose())

@pytest.fixture(scope="session")
def async_session_maker(async_engine):
    return async_sessionmaker(bind=async_engine, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db_session(async_session_maker):
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
async def client(db_session, monkeypatch):
    # Переопределяем зависимость session_getter
    async def override_session_getter():
        yield db_session
    monkeypatch.setattr(db_module.db_handler, "session_getter", override_session_getter)
    async with AsyncClient(
            transport=ASGITransport(app=main_app),
            base_url="http://test"
    ) as ac:
        yield ac




# TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope="session")
# async def engine():
#     engine = create_async_engine(TEST_DATABASE_URL, echo=False)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield engine
#     await engine.dispose()
#
#
# @pytest.fixture
# async def session(engine):
#     """Фикстура создает изолированную сессию для каждого теста"""
#     Session = async_sessionmaker(bind=engine, expire_on_commit=False)
#     async with Session() as session:
#         yield session
#
#
# @pytest.fixture
# async def ac(session):
#     """
#     ГЛАВНОЕ: Мы переопределяем session_getter так,
#     чтобы он возвращал уже открытую в тесте сессию.
#     """
#
#     async def _override_get_db():
#         yield session
#
#     # Заменяем оригинальную зависимость на нашу локальную
#     main_app.dependency_overrides[db_handler.session_getter] = _override_get_db
#
#     async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test") as client:
#         yield client
#
#     main_app.dependency_overrides.clear()











# import os
# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.testing import future
#
# from src.config.settings import Settings
# import asyncio
# from httpx import AsyncClient, ASGITransport
# from src.main import main_app
# from src.config.database import db_handler
# from src.models.base import Base
#
# from src.config.settings import get_settings
#
#
# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
#
#
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope="function", autouse=True)
# async def test_db():
#     # 1. Принудительно инициализируем db_handler тестовым URL ПЕРЕД запуском приложения
#     TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@test_db:5432/test_db"
#
#     from src.config.database import DatabaseAsyncHandler
#
#     test_db_handler = DatabaseAsyncHandler()
#     test_db_handler.init_db(
#         database_url=TEST_DATABASE_URL,
#         echo=False
#     )
#
#     # 2. Создаем таблицы
#     async with test_db_handler.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield
#
#     # 3. Очистка
#     async with db_handler.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#     await db_handler.dispose()
#
# @pytest.fixture(scope="function")
# def client(test_db):
#     from src.config.database import db_handler
#
#     def override_get_db():
#
#         yield test_db
#
#     main_app.
#
#
#
#     app.dependency_overrides[get_db] = override_get_db
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
#
# @pytest.fixture(scope="module")
# def client():
#     def override_get_db():
#         db =
#         try:
#             yield db
#         finally:
#             db.close()
#
#     app.dependency_overrides[get_db] = override_get_db
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
#
#
# # engine = create_engine(settings.sync_database_url)
# # TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# #
# #
# # @pytest.fixture(scope="module", autouse=True)
# # def setup_database():
# #     Base.metadata.create_all(bind=engine)
# #     yield
# #     Base.metadata.drop_all(bind=engine)
# #
# #
# # @pytest.fixture(scope="function")
# # def db_session():
# #     session = TestingSessionLocal()
# #     try:
# #         yield session
# #     finally:
# #         session.rollback()
# #         session.close()
# #
# #
# # @pytest.fixture(scope="module")
# # def client():
# #     def override_get_db():
# #         db = TestingSessionLocal()
# #         try:
# #             yield db
# #         finally:
# #             db.close()
# #
# #     app.dependency_overrides[get_db] = override_get_db
# #     client = TestClient(app)
# #     yield client
# #     app.dependency_overrides.clear()
#
#
#
#
# # @pytest.fixture(scope="session", autouse=True)
# # async def initialize_tests():
# #     # 1. Принудительно инициализируем db_handler тестовым URL ПЕРЕД запуском приложения
# #     TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@test_db:5432/test_db"
# #
# #     db_handler.init_db(
# #         database_url=TEST_DATABASE_URL,
# #         echo=False
# #     )
# #
# #     # 2. Создаем таблицы
# #     async with db_handler.engine.begin() as conn:
# #         await conn.run_sync(Base.metadata.create_all)
# #
# #     yield
# #
# #     # 3. Очистка
# #     async with db_handler.engine.begin() as conn:
# #         await conn.run_sync(Base.metadata.drop_all)
# #     await db_handler.dispose()
# #
# #
# # @pytest.fixture(scope="session")
# # async def ac():
# #     # Используем lifespan приложения (он подхватит уже инициализированный db_handler)
# #     async with AsyncClient(
# #             transport=ASGITransport(app=main_app),
# #             base_url="http://test"
# #     ) as client:
# #         yield client
# #
# #
# # @pytest.fixture(scope="session")
# # def anyio_backend():
# #     return "asyncio"
