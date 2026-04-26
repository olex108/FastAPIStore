# conftest.py
from src.config.database import db_handler
from src.dependencies.auth import AuthUserDependencies
from src.models import User
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
from src.utils.security import TokenHandler

import os
from dotenv import load_dotenv
from src.config.settings import get_settings

load_dotenv(dotenv_path=get_settings().BASE_DIR / ".env.test")

# ФИКСТУРЫ ДЛЯ СОЗДАНИЯ ПОДКЛЮЧЕНИЙ
TEST_DATABASE_URL = f"postgresql+asyncpg://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"


engine_test = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


# Переопределяем зависимость сессии для FastAPI
async def override_get_async_session():
    async with async_session_maker() as session:
        yield session


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
    # 1. Сначала применяем оверрайд сессии
    # Это гарантирует, что ПЕРЕД созданием клиента приложение уже знает про тестовую БД
    from src.main import main_app
    from src.config.database import db_handler

    main_app.dependency_overrides[db_handler.session_getter] = override_get_async_session

    # 2. Теперь создаем клиент
    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test"
    ) as ac:
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
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Генерируем токен
        token = TokenHandler.create_access_token(data={"sub": user.email})
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clean_auth_overrides():
    """
    Автоматическая очистка моков авторизации после каждого теста.

    Фикстура сохраняет в dependency_overrides только подключение к базе данных
    (session_getter), удаляя все остальные подмены (права доступа, текущий пользователь).
    Это гарантирует изоляцию тестов и предотвращает утечку прав доступа
    между тестами, при этом не ломая работу с тестовой БД.
    """

    yield
    # Получаем список всех ключей, кроме нашего session_getter
    to_delete = [
        k for k in main_app.dependency_overrides.keys()
        if k != db_handler.session_getter
    ]
    for k in to_delete:
        del main_app.dependency_overrides[k]


def get_mock_user():
    """Вспомогательный мок-объект"""

    return User(
        id=1,
        full_name="Mock Admin",
        email="admin@test.com",
        phone="+71111111111",
        is_active=True,
        is_superuser=True
    )
