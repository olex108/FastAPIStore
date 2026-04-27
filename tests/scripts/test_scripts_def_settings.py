import pytest
from sqlalchemy import select

from src.config.database import db_handler
from src.models import Permission, Role, RolePermissions
from src.scripts.default_roles_permissions_settings import TARGET_PERMISSIONS_ROLES, default_settings


@pytest.fixture
async def setup_sync_db(prepare_database):
    """
    Инициализируем db_handler тестовым URL и подменяем генератор сессий.
    """
    from tests.conftest import TEST_DATABASE_URL, async_session_maker

    # Инициализируем handler тестовыми настройками
    db_handler.init_db(database_url=TEST_DATABASE_URL, echo=False)

    # Подменяем session_getter на тестовый
    async def mock_session_getter():
        async with async_session_maker() as session:
            yield session

    original_getter = db_handler.session_getter
    db_handler.session_getter = mock_session_getter

    yield

    # Возвращаем всё как было
    db_handler.session_getter = original_getter


@pytest.mark.asyncio
async def test_sync_all_logic(setup_sync_db):
    """Тестируем основной сценарий синхронизации"""

    # 1. Запускаем скрипт
    await default_settings()

    # 2. Проверяем, что роли создались (используем session_getter напрямую для проверки)
    async for session in db_handler.session_getter():
        # Проверка ролей
        res_roles = await session.execute(select(Role))
        roles = res_roles.scalars().all()
        assert len(roles) == len(TARGET_PERMISSIONS_ROLES)

        # Проверка прав для роли Customer
        res_cust = await session.execute(
            select(Permission.name).join(RolePermissions).join(Role).where(Role.name == "Customer")
        )
        cust_perms = res_cust.scalars().all()
        assert cust_perms == ["products:view"]

        # Проверка Admin (что все права на месте)
        res_admin = await session.execute(
            select(Permission.name).join(RolePermissions).join(Role).where(Role.name == "Admin")
        )
        admin_perms = res_admin.scalars().all()
        assert len(admin_perms) == len(TARGET_PERMISSIONS_ROLES["Admin"])


@pytest.mark.asyncio
async def test_sync_removes_old_permissions(setup_sync_db):
    """Проверка удаления лишних разрешений, которых нет в TARGET_PERMISSIONS"""

    async for session in db_handler.session_getter():
        # Добавляем фейковое разрешение
        session.add(Permission(name="trash:permission"))
        await session.commit()

    # Запускаем синхронизацию
    await default_settings()

    async for session in db_handler.session_getter():
        res = await session.execute(select(Permission).where(Permission.name == "trash:permission"))
        assert res.scalar_one_or_none() is None
