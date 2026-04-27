import pytest

from src.models import User
from tests.conftest import async_session_maker

from fastapi import HTTPException

from src.dependencies.auth import AuthUserDependencies


@pytest.mark.asyncio
async def test_get_current_user_logic(auth_headers):
    from fastapi.security import HTTPAuthorizationCredentials

    from src.dependencies.auth import AuthUserDependencies

    token_str = auth_headers["Authorization"].split(" ")[1]
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)

    # Создаем сессию вручную для вызова зависимости
    async with async_session_maker() as session:
        user = await AuthUserDependencies.get_current_user(auth=creds, session=session)

        assert user.email == "test@example.com"
        assert user.is_active is True


@pytest.mark.asyncio
async def test_get_current_active_user_success():
    """Проверка: активный пользователь проходит успешно"""
    # Создаем мок-объект пользователя (в памяти, без БД)
    mock_user = User(full_name="Active User", email="active@test.com", is_active=True)

    # Вызываем метод напрямую
    result = await AuthUserDependencies.get_current_active_user(current_user=mock_user)

    assert result == mock_user
    assert result.is_active is True


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """Проверка: неактивный пользователь вызывает 403 ошибку"""
    mock_user = User(full_name="Inactive User", email="inactive@test.com", is_active=False)

    # Проверяем, что вызывается HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await AuthUserDependencies.get_current_active_user(current_user=mock_user)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Inactive user"
