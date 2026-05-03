import pytest
from fastapi import HTTPException
from src.utils.pagination import CursorHandler  # поправь путь импорта
from src.config.pagination import SortOptions
from src.models import Product, User


@pytest.mark.asyncio
class TestCursorHandler:

    # --- Тесты для get_cursor_data ---

    async def test_get_cursor_data_success(self):
        cursor = "SomeValue::123"
        result = await CursorHandler.get_cursor_data(cursor)
        assert result == ("SomeValue", 123)

    async def test_get_cursor_data_invalid_format(self):
        # Передаем некорректный курсор (нет разделителя ::)
        with pytest.raises(HTTPException) as exc:
            await CursorHandler.get_cursor_data("invalid_cursor")
        assert exc.value.status_code == 400
        assert exc.value.detail == "Incorrect cursor format"

    # --- Тесты для get_next_cursor_product ---

    async def test_get_next_cursor_product_name(self):
        # Создаем мок-объект продукта
        product = Product(id=10, name="Apple", price=100.0)

        cursor = await CursorHandler.get_next_cursor_product(product, SortOptions.name_asc)
        assert cursor == "Apple::10"

    async def test_get_next_cursor_product_price(self):
        product = Product(id=10, name="Apple", price=100.0)

        # Предполагаем, что любой другой вариант sort_by вернет цену
        cursor = await CursorHandler.get_next_cursor_product(product, SortOptions.price_asc)
        assert cursor == "100.0::10"

    # --- Тесты для get_next_cursor_user ---

    async def test_get_next_cursor_user_success(self):
        user = User(id=5, full_name="John Doe")

        cursor = await CursorHandler.get_next_cursor_user(user)
        assert cursor == "John Doe::5"

    async def test_get_next_cursor_user_exception(self):
        # Проверка обработки ошибки, если у объекта нет нужных атрибутов
        with pytest.raises(
                AttributeError):  # В коде try-except ловит ValueError, но отсутствие атрибута - это AttributeError
            await CursorHandler.get_next_cursor_user(None)
