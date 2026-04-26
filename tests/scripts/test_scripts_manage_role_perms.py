import pytest
from unittest.mock import patch
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Импортируем модели и скрипт
from src.models import Role, Permission, RolePermissions
from src.scripts.manage_role_perms import interactive_shell
from src.config.database import db_handler


@pytest.fixture
async def seed_data(prepare_database):
    """Наполняем базу начальными данными перед тестом"""
    from tests.conftest import async_session_maker

    async with async_session_maker() as session:
        role = Role(name="TestRole")
        perm1 = Permission(name="perm:one")
        perm2 = Permission(name="perm:two")

        session.add_all([role, perm1, perm2])
        await session.commit()

        # Обновляем объекты, чтобы получить их ID из базы
        await session.refresh(role)
        await session.refresh(perm1)
        await session.refresh(perm2)
        return role, perm1, perm2


@pytest.mark.asyncio
async def test_add_permission_flow(seed_data, monkeypatch):
    """Тест сценария: Выбрать роль -> Добавить разрешение -> Выйти"""
    role, perm1, perm2 = seed_data
    from tests.conftest import async_session_maker

    # 1. Подменяем сессию в db_handler, чтобы скрипт юзал тестовую БД
    async def mock_session_getter():
        async with async_session_maker() as session:
            yield session

    monkeypatch.setattr(db_handler, "session_getter", mock_session_getter)

    # 2. Настраиваем последовательность ввода:
    # {ID роли} -> '+' (добавить) -> {ID разрешения} -> 'b' (назад) -> '0' (выход)
    user_inputs = [str(role.id), "+", str(perm1.id), "b", "0"]

    with patch("builtins.input", side_effect=user_inputs), patch("builtins.print"):
        await interactive_shell()

    # 3. Проверяем, что связь реально появилась в БД
    async with async_session_maker() as session:
        res = await session.execute(
            select(RolePermissions).where(
                RolePermissions.role_id == role.id, RolePermissions.permission_id == perm1.id
            )
        )
        link = res.scalar_one_or_none()
        assert link is not None


@pytest.mark.asyncio
async def test_remove_permission_flow(seed_data, monkeypatch):
    """Тест сценария: Удалить существующее разрешение"""
    role, perm1, perm2 = seed_data
    from tests.conftest import async_session_maker

    # Сначала создаем связь вручную, чтобы было что удалять
    async with async_session_maker() as session:
        session.add(RolePermissions(role_id=role.id, permission_id=perm1.id))
        await session.commit()

    async def mock_session_getter():
        async with async_session_maker() as session:
            yield session

    monkeypatch.setattr(db_handler, "session_getter", mock_session_getter)

    # Ввод: {ID роли} -> '-' (удалить) -> {ID разрешения} -> 'b' -> '0'
    user_inputs = [str(role.id), "-", str(perm1.id), "b", "0"]

    with patch("builtins.input", side_effect=user_inputs), patch("builtins.print"):
        await interactive_shell()

    # Проверяем, что связи больше нет
    async with async_session_maker() as session:
        res = await session.execute(select(RolePermissions).where(RolePermissions.role_id == role.id))
        assert res.scalar_one_or_none() is None
