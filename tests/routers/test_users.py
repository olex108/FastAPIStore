import pytest
from httpx import AsyncClient
from src.main import main_app
from src.dependencies.permissions import PermissionChecker
from src.dependencies.auth import AuthUserDependencies
from src.models.user import User
from tests.conftest import async_session_maker, get_mock_user


@pytest.mark.asyncio
async def test_get_users(ac: AsyncClient):
    """Тест просмотра списка пользователей"""
    mock_user = get_mock_user()

    # Мокаем права. База (session_getter) уже подменена в conftest.py
    main_app.dependency_overrides[PermissionChecker(["users:view"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user

    response = await ac.get("/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_current_user_info_me(ac: AsyncClient):
    """Тест получения информации о себе"""

    mock_user = get_mock_user()

    # Мокаем получение пользователя
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    response = await ac.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == mock_user.email


@pytest.mark.asyncio
async def test_get_user_by_id(ac: AsyncClient):
    """Тест получения пользователя по ID"""

    # Создаем пользователя в ТЕСТОВОЙ БД
    async with async_session_maker() as session:
        new_user = User(
            full_name="Target User",
            email="target@test.com",
            phone="+72222222222",
            hashed_password="fake",
            is_active=True
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        target_id = new_user.id

    mock_user = get_mock_user()

    # Мокаем права доступа
    main_app.dependency_overrides[PermissionChecker(["users:view"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    response = await ac.get(f"/users/{target_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_id
    assert data["full_name"] == "Target User"
