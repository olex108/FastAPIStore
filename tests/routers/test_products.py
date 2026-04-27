import pytest
from httpx import AsyncClient

from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker
from src.main import main_app
from src.models.product import Product
from tests.conftest import async_session_maker, get_mock_user


# 1. Тест создания продукта (POST)
@pytest.mark.asyncio
async def test_create_product(ac: AsyncClient):
    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:create"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    product_data = {"name": "Smartphone", "quantity": 10000, "price": 1000, "is_active": True}

    response = await ac.post("/products/", json=product_data)

    assert response.status_code == 200
    assert response.json()["name"] == "Smartphone"


# 2. Тест получения списка (GET)
@pytest.mark.asyncio
async def test_get_products_list(ac: AsyncClient):
    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:view"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    response = await ac.get("/products/")
    assert response.status_code == 200
    assert response.json()["next_cursor"] is None
    assert isinstance(response.json()["items"], list)


# 3. Тест получения по ID + 404 (GET)
@pytest.mark.asyncio
async def test_get_product_by_id(ac: AsyncClient):
    # Создаем продукт
    async with async_session_maker() as session:
        product = Product(name="Item", quantity=10000, price=1000, is_active=True)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        p_id = product.id

    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:view"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    # Успешный поиск
    resp = await ac.get(f"/products/{p_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Item"

    # Поиск несуществующего (ID 9999)
    resp_404 = await ac.get("/products/9999")
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Product not found"


# 4. Тест обновления (PUT)
@pytest.mark.asyncio
async def test_update_product(ac: AsyncClient):
    async with async_session_maker() as session:
        product = Product(name="Old Item", quantity=10000, price=1000, is_active=True)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        p_id = product.id

    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:update"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    update_data = {"name": "New Item", "quantity": 10000, "price": 1000, "is_active": True}
    response = await ac.put(f"/products/{p_id}", json=update_data)

    assert response.status_code == 200
    assert response.json()["name"] == "New Item"

    # Удаление несуществующего (ID 9999)
    resp_404 = await ac.put("/products/9999", json=update_data)
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Product not found"


# 5. Тест удаления (DELETE)
@pytest.mark.asyncio
async def test_delete_product(ac: AsyncClient):
    async with async_session_maker() as session:
        product = Product(name="Item", quantity=10000, price=1000, is_active=True)
        session.add(product)
        await session.commit()
        await session.refresh(product)
        p_id = product.id

    mock_user = get_mock_user()
    main_app.dependency_overrides[PermissionChecker(["products:delete"])] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    response = await ac.delete(f"/products/{p_id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

    # Удаление несуществующего (ID 9999)
    resp_404 = await ac.delete("/products/9999")
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Product not found"
