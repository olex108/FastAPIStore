# conftest.py

from src.config.database import db_handler
from src.models.base import Base
import asyncio
from src.main import main_app
import pytest
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from sqlalchemy.pool import NullPool
import sqlalchemy as sa

from src.models.user import Permission, Role, User
from src.utils.security import TokenHandler  # Импортируйте ваш обработчик


# Используем SQLite в памяти для простоты тестов, либо другую тестовую БД Postgres
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:ae35ad@localhost:5432/test_db"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


# Переопределяем зависимость сессии для FastAPI
async def override_get_async_session():
    async with async_session_maker() as session:
        yield session


main_app.dependency_overrides[db_handler.session_getter] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Создаем таблицы
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем таблицы и ПРИНУДИТЕЛЬНО закрываем соединения
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def clean_tables():
    """Фикстура очистки данных во всех таблицах перед каждым тестом."""
    yield  # Сначала выполняется сам тест

    # После теста очищаем данные
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(sa.text(f"TRUNCATE {table.name} CASCADE;"))

# ФИКСТУРЫ ДАННЫХ

# Сборка дерева прав пользователя
@pytest.fixture
async def create_permission(session: AsyncSession):
    async def _create(name: str):
        perm = Permission(name=name)
        session.add(perm)
        await session.commit()
        return perm
    return _create

@pytest.fixture
async def create_role(session: AsyncSession):
    async def _create(name: str, permissions: list = None):
        role = Role(name=name)
        if permissions:
            role.permissions = permissions
        session.add(role)
        await session.commit()
        return role
    return _create


# Фикстура авторизации
@pytest.fixture
async def auth_headers():
    """
    Создает пользователя и возвращает заголовок с токеном.
    Используем фабрику сессий напрямую, чтобы избежать проблем с loop.
    """
    # Создаем сессию через вашу рабочую фабрику
    async with async_session_maker() as session:
        user = User(
            full_name="Test User",
            email="test@example.com",
            phone="+79991234567",
            hashed_password="fake_hash",
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Генерируем токен
        token = TokenHandler.create_access_token(data={"sub": user.email})
        return {"Authorization": f"Bearer {token}"}

