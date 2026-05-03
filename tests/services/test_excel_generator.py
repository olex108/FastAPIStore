import os
from pathlib import Path
from datetime import datetime
import pytest
from src.services.excel_receipt_generator import generate_receipt_excel
from src.schemas.cart import CartOut, CartProductsOut, ProductInfo
from src.models.cart import CartStatus
from src.models.order import Contacts
from src.models.user import User

from src.config.settings import get_settings


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def mock_user():
    return User(
        id=1,
        full_name="Иван Иванов",
        phone="+79991234567",
        email="test@example.com"
    )


@pytest.fixture
def mock_contacts():
    return Contacts(
        name="ООО Тест Компани",
        inn="1234567890",
        address="г. Москва, ул. Тестовая, д. 1"
    )


@pytest.fixture
def mock_cart_out():
    # Создаем данные для вложенных товаров
    product_item = CartProductsOut(
        product=ProductInfo(id=101, name="Тестовый товар", price=1500.0, quantity=10, is_active=True),
        product_quantity=2,
        product_price=1500.0,  # в Pydantic это может вычисляться, но для теста укажем явно
        product_amount=3000.0
    )

    return CartOut(
        id=7,
        user_id=1,
        status=CartStatus.CURRENT,
        order_at=datetime(2026, 4, 28, 14, 0, 0),
        products=[product_item],
        amount=3000.0
    )


def test_generate_receipt_excel_creates_file(mock_cart_out, mock_contacts, mock_user, settings):
    # Вызываем функцию
    relative_path = generate_receipt_excel(mock_cart_out, mock_contacts, mock_user)

    # 1. Проверяем формат возвращаемого пути
    assert relative_path.startswith("media/orders/receipt_")
    assert relative_path.endswith(".xlsx")

    # 2. Проверяем физическое наличие файла
    full_path = Path(settings.BASE_DIR) / relative_path
    assert full_path.exists()
    assert full_path.is_file()

    # 3. Проверяем, что файл не пустой (размер > 0 байт)
    assert full_path.stat().st_size > 0

    # Очистка после теста (необязательно, если папка media в gitignore)
    # os.remove(full_path)


def test_generate_receipt_excel_content_integrity(mock_cart_out, mock_contacts, mock_user, settings):
    # Тест на случай отсутствия контактов (проверка блока try-except в функции)
    mock_contacts.name = None
    mock_contacts.inn = None

    relative_path = generate_receipt_excel(mock_cart_out, mock_contacts, mock_user)
    full_path = Path(settings.BASE_DIR) / relative_path

    assert full_path.exists()
