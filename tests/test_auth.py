from fastapi import status

# Пример данных для регистрации пользователя
user_register_data = {
    "email": "test@example.com",
    "phone": "+79991234567",
    "password": "Password!",
    "full_name": "Test User",
    "confirm_password": "Password!"
}

async def test_register_user(client):
    response = await client.post("/users/register", json=user_register_data)
    assert response.status_code == status.HTTP_201_CREATED  # Ожидаем статус 201
    assert "email" in response.json()  # Убедимся, что поле username присутствует

    # Дополнительные проверки для других случаев исключений
    # Например, тест для существующего пользователя:
    # await client.post("/users/register", json=user_register_data)
    # response = await client.post("/users/register", json=user_register_data)
    # assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем статус 400, если пользователь уже существует

    # Пример проверки на неверные данные
    # invalid_user_data = {...}
    # response = await client.post("/users/register", json=invalid_user_data)
    # assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Ожидаем статус 422

import pytest
from httpx import AsyncClient


# @pytest.mark.asyncio
# async def test_auth_full_cycle(ac: AsyncClient):
#     """
#     Комплексный тест: Регистрация -> Логин -> Refresh
#     Этот тест покроет сразу 3 эндпоинта.
#     """
#
#     # --- 1. ТЕСТ РЕГИСТРАЦИИ ---
#     user_data = {
#         "email": "test@example.com",
#         "phone": "+79991234567",
#         "password": "Password!",
#         "full_name": "Test User",
#         "confirm_password": "Password!"
#     }
#     # У тебя префикс /users для регистрации
#     reg_response = await ac.post("/users/register", json=user_data)
#     assert reg_response.status_code == 200
#     assert reg_response.json()["email"] == user_data["email"]
#
#     # --- 2. ТЕСТ ЛОГИНА ---
#     login_data = {
#         "user": user_data["email"],  # Поле 'user' из твоей схемы UserLogin
#         "password": user_data["password"]
#     }
#     login_response = await ac.post("/auth/login", json=login_data)
#     assert login_response.status_code == 200
#     tokens = login_response.json()
#     assert "access_token" in tokens
#     assert "refresh_token" in tokens
#
#     refresh_token = tokens["refresh_token"]
#
#     # --- 3. ТЕСТ REFRESH TOKEN ---
#     # Передаем refresh_token в заголовке, как требует твой эндпоинт
#     refresh_response = await ac.post(
#         "/auth/refresh",
#         headers={"refresh-token": refresh_token}
#     )
#     assert refresh_response.status_code == 200
#     assert "access_token" in refresh_response.json()
#
#
# @pytest.mark.asyncio
# async def test_login_wrong_password(ac: AsyncClient):
#     """Тест на неверный пароль (проверка 401 ошибки)"""
#     login_data = {
#         "user": "test@example.com",
#         "password": "wrong_password"
#     }
#     response = await ac.post("/auth/login", json=login_data)
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Incorrect email, phone or password"
#
#
# @pytest.mark.asyncio
# async def test_refresh_invalid_token(ac: AsyncClient):
#     """Тест на невалидный refresh токен"""
#     response = await ac.post(
#         "/auth/refresh",
#         headers={"refresh-token": "not-a-real-token"}
#     )
#     assert response.status_code == 401
