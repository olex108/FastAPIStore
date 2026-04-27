from typing import List

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.models.cart import CartStatus


class ProductInfo(BaseModel):
    """Схема для возвращения информации о товаре"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float
    quantity: int
    is_active: bool


class CartProductsOut(BaseModel):
    """Схема для списка товаров"""

    model_config = ConfigDict(from_attributes=True)

    product: "ProductInfo"

    your_price: float | None = Field(None, alias="product_price")
    product_quantity: int
    amount: int | None = Field(None, alias="product_amount")

    @computed_field
    def available(self) -> str:
        """
        Метод для проверки наличия достаточного количества единиц продукта для заказа.
        Возвращает вариант наличия продукта
        """

        if self.product.quantity == 0 or not self.product.is_active:
            return "Out of stock"
        elif self.product_quantity < self.product.quantity:
            return "In stock"
        else:
            return f"{self.product.quantity} available"

    @computed_field
    def product_price(self) -> float:
        """Метод для получения стоимости товара"""

        if self.your_price is not None:
            return self.your_price
        return self.product.price

    @computed_field
    def product_amount(self) -> float:
        """
        Метод для получения стоимости товара
        если сумма в корзине None, вычисляем (цена * кол-во)
        """

        if self.amount is not None:
            return self.amount
        return self.product_price * self.product_quantity


class CartOut(BaseModel):
    """
    Схема для возвращения корзины.
    Содержит вложенный список из схемы CartProductsOut и вложенной схемы ProductInfo
    """

    id: int
    user_id: int
    status: CartStatus

    products: List[CartProductsOut]

    @computed_field
    def amount(self) -> float:
        """Метод для получения стоимости товаров в корзине"""
        return sum(item.product_amount for item in self.products if item.product_amount)


class ProductAdd(BaseModel):
    """Схема для добавления продукта в корзину"""

    product_id: int
    product_quantity: int
