import pytest
from httpx import AsyncClient

from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import OwnerOrPermissionChecker
from src.main import main_app
from src.models.cart import Cart, CartProducts, CartStatus
from src.models.product import Product
from src.models.user import User
from tests.conftest import async_session_maker, get_mock_user
import src.routers.cart as cart_router


@pytest.mark.asyncio
async def test_get_current_user_cart_me(ac: AsyncClient):
    # 1. Создаем структуру данных в БД
    async with async_session_maker() as session:
        # Пользователь
        user = User(
            id=1, full_name="Cart Owner", email="cart@test.com", phone="+71111111111", hashed_password="test", is_active=True
        )
        session.add(user)
        await session.flush()  # Получаем user.id

        # Продукт
        prod = Product(id=1, name="Test Item", price=100.0, quantity=10, is_active=True)
        session.add(prod)
        await session.flush()

        # Корзина
        cart = Cart(id=1, user_id=user.id, status="current")  # Укажите ваш CartStatus
        session.add(cart)
        await session.flush()

        # Товар в корзине
        cart_prod = CartProducts(cart_id=cart.id, product_id=prod.id, product_quantity=2)
        session.add(cart_prod)
        await session.commit()
        user_id = user.id


    # 2. Мокаем авторизацию (передаем созданного пользователя)
    mock_user = user
    mock_user.id = user_id
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    # 3. Запрос
    response = await ac.get("/carts/me")

    assert response.status_code == 200
    data = response.json()

    # Проверяем вычисляемые поля
    assert data["user_id"] == user_id
    assert len(data["products"]) == 1
    assert data["products"][0]["product_amount"] == 200.0  # 100 * 2
    assert data["amount"] == 200.0  # Сумма всей корзины
    assert data["products"][0]["available"] == "In stock"


@pytest.mark.asyncio
async def test_get_cart_by_user_id_as_admin(ac: AsyncClient):
    # 1. Создаем корзину чужого пользователя
    async with async_session_maker() as session:
        other_user = User(
            full_name="Other", email="other@test.com", phone="+72222222222", hashed_password="test", is_active=True
        )
        session.add(other_user)
        await session.flush()

        cart = Cart(user_id=other_user.id, status="current")
        session.add(cart)
        await session.commit()
        other_user_id = other_user.id

    # 2. Мокаем OwnerOrPermissionChecker так, будто запрос делает админ
    mock_admin = get_mock_user()  # Наш дефолтный мок-админ
    main_app.dependency_overrides[OwnerOrPermissionChecker(["carts:view"])] = lambda: mock_admin
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_admin
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_admin

    # 3. Запрос к чужой корзине
    response = await ac.get(f"/carts/{other_user_id}")

    assert response.status_code == 200
    assert response.json()["user_id"] == other_user_id


@pytest.mark.asyncio
async def test_get_cart_error_500(ac: AsyncClient, monkeypatch):
    mock_user = get_mock_user()
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    # Мокаем функцию из CRUD, чтобы она выкинула исключение
    async def mock_get_user_cart_fail(*args, **kwargs):
        raise Exception("Database Connection Lost")

    # Патчим функцию именно там, где её вызывает роутер
    monkeypatch.setattr(cart_router, "get_user_cart", mock_get_user_cart_fail)

    response = await ac.get("/carts/me")

    assert response.status_code == 500
    assert response.json()["detail"] == "Can`t get cart data"


@pytest.mark.asyncio
async def test_add_product_to_me_success(ac: AsyncClient):
    """Тест добавления одного товара в свою корзину"""

    async with async_session_maker() as session:
        user = User(full_name="Me", email="me@test.com", phone="+71111111111", hashed_password="f", is_active=True)
        session.add(user)
        await session.flush()

        cart = Cart(user_id=user.id, status=CartStatus.CURRENT)
        session.add(cart)

        prod = Product(name="Item", price=100.0, quantity=10, is_active=True)
        session.add(prod)
        await session.commit()
        await session.refresh(user)
        await session.refresh(cart)

    mock_user = user
    mock_user.cart = cart

    # Мокаем зависимости
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user

    payload = {"product_id": prod.id, "product_quantity": 2}
    response = await ac.post("/carts/me/add_product", json=payload)

    assert response.status_code == 200
    assert response.json()["products"][0]["product_quantity"] == 2


@pytest.mark.asyncio
async def test_add_user_product_by_id_success(ac: AsyncClient):
    """Тест добавления товара в корзину по user_id (админом или владельцем)"""
    async with async_session_maker() as session:
        target_user = User(
            full_name="Target", email="t@t.com", phone="+72222222222", hashed_password="f", is_active=True
        )
        session.add(target_user)
        await session.flush()

        cart = Cart(user_id=target_user.id, status=CartStatus.CURRENT)
        session.add(cart)

        prod = Product(name="Target Item", price=50.0, quantity=5, is_active=True)
        session.add(prod)
        await session.commit()
        target_id = target_user.id
        prod_id = prod.id

    mock_admin = get_mock_user()
    # Мокаем чекер (так как в URL есть {user_id}, FastAPI сам его подставит в зависимость)
    main_app.dependency_overrides[OwnerOrPermissionChecker] = lambda: mock_admin
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_admin

    payload = {"product_id": prod_id, "product_quantity": 1}
    # Здесь user_id идет в путь
    response = await ac.post(f"/carts/{target_id}/add_product", json=payload)

    assert response.status_code == 200
    assert response.json()["user_id"] == target_id


@pytest.mark.asyncio
async def test_add_products_list_to_me_success(ac: AsyncClient):
    """Тест добавления списка товаров (исправляем 422 через params)"""
    async with async_session_maker() as session:
        user = User(full_name="ListMe", email="l@m.com", phone="3", hashed_password="f", is_active=True)
        session.add(user)
        await session.flush()

        cart = Cart(user_id=user.id, status=CartStatus.CURRENT)
        session.add(cart)

        p1 = Product(name="P1", price=10, quantity=10, is_active=True)
        p2 = Product(name="P2", price=20, quantity=10, is_active=True)
        session.add_all([p1, p2])
        await session.commit()
        await session.refresh(user)
        await session.refresh(cart)

    mock_user = user
    mock_user.cart = cart

    main_app.dependency_overrides[OwnerOrPermissionChecker] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user

    payload = [{"product_id": p1.id, "product_quantity": 1}, {"product_id": p2.id, "product_quantity": 3}]

    # Добавляем params={"user_id": user.id}, чтобы удовлетворить сигнатуру OwnerOrPermissionChecker
    response = await ac.post("/carts/me/add_products", json=payload, params={"user_id": user.id})

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 2
    assert data["amount"] == 70.0  # (10*1) + (20*3)


@pytest.mark.asyncio
async def test_add_products_list_success(ac: AsyncClient):
    """Тест добавления списка товаров в корзину текущего пользователя"""

    async with async_session_maker() as session:
        user = User(
            full_name="Cart Owner", email="cart@test.com", phone="+71111111111", hashed_password="test", is_active=True
        )
        session.add(user)
        await session.commit()
        await session.rollback()  # Получаем user.id

        # Корзина
        cart = Cart(user_id=user.id, status=CartStatus.CURRENT)
        session.add(cart)
        await session.commit()
        await session.rollback()

        p1 = Product(name="P1", price=10, quantity=10, is_active=True)
        p2 = Product(name="P2", price=20, quantity=10, is_active=True)
        session.add_all([p1, p2])
        await session.commit()

        p1_id, p2_id = p1.id, p2.id

    mock_user = user
    mock_user.cart = cart

    main_app.dependency_overrides[AuthUserDependencies.get_current_active_user] = lambda: mock_user
    main_app.dependency_overrides[AuthUserDependencies.get_current_user] = lambda: mock_user

    payload = [{"product_id": p1_id, "product_quantity": 2}, {"product_id": p2_id, "product_quantity": 5}]

    response = await ac.post("/carts/me/add_products", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 2
    # Общая сумма: (10*2) + (20*5) = 120
    assert data["amount"] == 120.0
