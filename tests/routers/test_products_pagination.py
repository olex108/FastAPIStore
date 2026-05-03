import pytest
from httpx import AsyncClient
from sqlalchemy.dialects.postgresql import insert

from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker
from src.main import main_app
from src.models.product import Product
from tests.conftest import async_session_maker, get_mock_user


@pytest.fixture
async def create_test_products():
    products = [
        {"name": "Apple iPhone", "price": 1000, "quantity": 1000, "is_active": True},
        {"name": "Samsung Galaxy", "price": 800, "quantity": 1000, "is_active": True},
        {"name": "Apple MacBook", "price": 2000, "quantity": 1000, "is_active": True},
        {"name": "Xiaomi Mi", "price": 500, "quantity": 1000, "is_active": True},
    ]

    async with async_session_maker() as session:
        stmt = insert(Product).values(products)

        await session.execute(stmt)
        await session.commit()

        return


@pytest.mark.asyncio
async def test_products_pagination_and_sorting(ac: AsyncClient, create_test_products):
    # Устанавливаем моки
    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:create"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    # 1. Тест лимита
    response = await ac.get("/products/", params={"limit": 2})
    data = response.json()
    assert len(data["items"]) == 2
    assert data["next_cursor"] is not None  # Так как товаров больше, чем 2

    # 2. Тест сортировки по цене (возрастание)
    response = await ac.get("/products/", params={"sort_by": "price_asc"})
    items = response.json()["items"]
    prices = [item["price"] for item in items]
    assert prices == sorted(prices)

    # 3. Тест фильтрации по имени
    response = await ac.get("/products/", params={"name_query": "Apple"})
    items = response.json()["items"]
    assert len(items) == 2
    assert all("Apple" in item["name"] for item in items)

    # 4. Тест логики курсора
    # Сначала берем первую страницу
    res1 = await ac.get("/products/", params={"limit": 1, "sort_by": "price_asc"})
    cursor = res1.json()["next_cursor"]

    # Запрашиваем вторую страницу, передавая курсор
    res2 = await ac.get("/products/", params={"limit": 1, "sort_by": "price_asc", "cursor": cursor})

    item1_id = res1.json()["items"][0]["id"]
    item2_id = res2.json()["items"][0]["id"]
    assert item1_id != item2_id
    assert res2.json()["items"][0]["price"] >= res1.json()["items"][0]["price"]


@pytest.mark.asyncio
async def test_products_invalid_cursor(ac: AsyncClient, create_test_products):

    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:create"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    # Тест на некорректный формат курсора (должен вернуть 400)
    response = await ac.get("/products/", params={"cursor": "invalid_string_without_separator"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect cursor format"
