import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import insert

from src.models.user import User
from tests.conftest import async_session_maker


@pytest.fixture
async def create_test_products():
    users = [
        {
            "full_name": "Alice",
            "email": "target1@test.com",
            "phone": "72222222221",
            "hashed_password": "fake",
            "is_active": True,
        },
        {
            "full_name": "Bob",
            "email": "target2@test.com",
            "phone": "72222222222",
            "hashed_password": "fake",
            "is_active": True,
        },
        {
            "full_name": "Charlie",
            "email": "target3@test.com",
            "phone": "72222222223",
            "hashed_password": "fake",
            "is_active": True,
        },
        {
            "full_name": "David",
            "email": "target4@test.com",
            "phone": "72222222224",
            "hashed_password": "fake",
            "is_active": True,
        },
    ]

    async with async_session_maker() as session:
        stmt = insert(User).values(users)

        await session.execute(stmt)
        await session.commit()

        return


@pytest.mark.asyncio
async def test_get_users_pagination_flow(ac: AsyncClient, create_test_products):
    """
    Тестируем полный цикл: лимит, фильтрацию и переход по курсору.
    """

    # 1. Проверяем фильтрацию по части имени (name_query)
    response = await ac.get("/users/", params={"name_query": "li"})
    assert response.status_code == 200
    items = response.json()["items"]
    # Должны найти Alice и Charlie
    assert len(items) == 2
    assert any(u["full_name"] == "Alice" for u in items)

    # 2. Проверяем лимит
    limit = 2
    response = await ac.get("/users/", params={"limit": limit})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == limit
    assert data["next_cursor"] is not None  # Есть еще пользователи

    # 3. Проверяем переход по курсору (Пагинация)
    # Берем первую страницу
    first_page = await ac.get("/users/", params={"limit": 2})
    cursor = first_page.json()["next_cursor"]
    last_user_first_page = first_page.json()["items"][-1]
    #
    # Запрашиваем вторую страницу с полученным курсором
    second_page = await ac.get("/users/", params={"limit": 2, "cursor": cursor})
    assert second_page.status_code == 200

    second_page_items = second_page.json()["items"]
    # Первый пользователь второй страницы не должен совпадать с последним первой
    assert second_page_items[0]["id"] != last_user_first_page["id"]
    # И по алфавиту он должен идти позже (так как у нас name_asc)
    assert second_page_items[0]["full_name"] >= last_user_first_page["full_name"]


@pytest.mark.asyncio
async def test_get_users_invalid_cursor(ac: AsyncClient):
    """Тест на отправку сломанного курсора"""
    # Отправляем строку без разделителя '::'
    response = await ac.get("/users/", params={"cursor": "invalid-cursor-format"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect cursor format"


@pytest.mark.asyncio
async def test_get_users_empty_next_cursor(ac: AsyncClient):
    """Проверяем, что next_cursor равен None, если данных больше нет и ошибку превышения лимита"""
    # Запрашиваем очень большой лимит, чтобы точно забрать всех
    response = await ac.get("/users/", params={"limit": 100})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    response = await ac.get("/users/", params={"limit": 10})
    assert response.status_code == 200
    assert response.json()["next_cursor"] is None
