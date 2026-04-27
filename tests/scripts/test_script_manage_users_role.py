from unittest.mock import patch

import pytest
from sqlalchemy import select

from src.config.database import db_handler
# Импортируем модели и скрипт
from src.models import Role, RoleUsers, User
from src.scripts.manage_users_role import interactive_user_roles


@pytest.fixture
async def seed_users_data(prepare_database):
    """Наполняем базу ролями и пользователями согласно актуальной модели User"""
    from tests.conftest import async_session_maker

    async with async_session_maker() as session:
        role = Role(name="Admin")

        # Создаем пользователей с учетом новых полей: phone и hashed_password
        user1 = User(
            full_name="Ivan Ivanov",
            email="ivan@test.com",
            phone="+79991112233",
            hashed_password="fake_hash_1",
            is_active=True,
        )
        user2 = User(
            full_name="Petr Petrov",
            email="petr@test.com",
            phone="+79994445566",
            hashed_password="fake_hash_2",
            is_active=True,
        )

        session.add_all([role, user1, user2])
        await session.commit()

        await session.refresh(role)
        await session.refresh(user1)
        await session.refresh(user2)
        return role, user1, user2


@pytest.mark.asyncio
async def test_add_user_to_role_by_phone_logic(seed_users_data, monkeypatch):
    """
    Дополнительный тест: проверяем, что поиск по ID работает,
    так как phone в get_user_by_identity сейчас не задействован напрямую,
    но мы проверяем корректность создания связей с новой моделью.
    """
    role, user1, user2 = seed_users_data
    from tests.conftest import async_session_maker

    async def mock_session_getter():
        async with async_session_maker() as session:
            yield session

    monkeypatch.setattr(db_handler, "session_getter", mock_session_getter)

    # Ввод: ID роли -> '+' -> ID юзера (через isdigit()) -> 'b' -> '0'
    user_inputs = [str(role.id), "+", str(user2.id), "b", "0"]

    with patch("builtins.input", side_effect=user_inputs), patch("builtins.print"):
        await interactive_user_roles()

    async with async_session_maker() as session:
        res = await session.execute(
            select(RoleUsers).where(RoleUsers.role_id == role.id, RoleUsers.user_id == user2.id)
        )
        assert res.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_add_user_to_role_by_email(seed_users_data, monkeypatch):
    role, user1, user2 = seed_users_data
    from tests.conftest import async_session_maker

    async def mock_session_getter():
        async with async_session_maker() as session:
            yield session

    monkeypatch.setattr(db_handler, "session_getter", mock_session_getter)

    user_inputs = [str(role.id), "+", user1.email, "b", "0"]

    with patch("builtins.input", side_effect=user_inputs), patch("builtins.print"):
        await interactive_user_roles()

    async with async_session_maker() as session:
        res = await session.execute(
            select(RoleUsers).where(
                RoleUsers.user_id == user1.id, RoleUsers.role_id == role.id  # Исправлено здесь  # Исправлено здесь
            )
        )
        assert res.scalar_one_or_none() is not None
