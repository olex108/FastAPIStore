from copy import copy

import pytest
from httpx import AsyncClient

from fastapi import status

# Пример данных для регистрации пользователя
user_register_data = {
    "email": "test@example.com",
    "phone": "+79991234567",
    "password": "Password!",
    "full_name": "Test User",
    "confirm_password": "Password!",
}


@pytest.mark.asyncio
async def test_register_user(ac):
    response = await ac.post("/users/register", json=user_register_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "email" in response.json()

    # тест для существующего пользователя
    response = await ac.post("/users/register", json=user_register_data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_register_user_validators(ac):
    # invalid email
    email_reg_data = copy(user_register_data)
    email_reg_data["email"] = "testexample.com"
    response = await ac.post("/users/register", json=email_reg_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid email address: An email address must have an @-sign."
    )

    # invalid phone
    phone_reg_data = copy(user_register_data)
    phone_reg_data["phone"] = "9991234567a"
    response = await ac.post("/users/register", json=phone_reg_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["msg"] == "Value error, Номер телефона должен начинаться с +7"

    # invalid password
    pass_reg_data = copy(user_register_data)
    pass_reg_data["password"] = "PASSWORD"

    response = await ac.post("/users/register", json=pass_reg_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert (
        response.json()["detail"][0]["msg"] == "Value error, Пароль должен содержать хотя бы один спецсимвол ($%&!:)"
    )


async def register_user(ac):
    await ac.post("/users/register", json=user_register_data)


@pytest.mark.asyncio
async def test_auth(ac):
    # Создаем пользователя
    await register_user(ac)

    # ТЕСТ ЛОГИНА
    login_data = {"user": user_register_data["email"], "password": user_register_data["password"]}

    login_response = await ac.post("/auth/login", json=login_data)

    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    refresh_token = tokens["refresh_token"]

    # --- 3. ТЕСТ REFRESH TOKEN ---
    # Передаем refresh_token в заголовке, как требует твой эндпоинт
    refresh_response = await ac.post("/auth/refresh", headers={"refresh-token": refresh_token})
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


@pytest.mark.asyncio
async def test_login_wrong_email(ac):
    login_data = {"user": "test@example.com", "password": "wrong_password"}
    response = await ac.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email, phone or password"


@pytest.mark.asyncio
async def test_login_wrong_password(ac):
    await register_user(ac)
    login_data = {"user": "test@example.com", "password": "wrong_password"}
    response = await ac.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email, phone or password"


@pytest.mark.asyncio
async def test_refresh_invalid_token(ac: AsyncClient):
    response = await ac.post("/auth/refresh", headers={"refresh-token": "not-a-real-token"})
    assert response.status_code == 401
