from typing import List

from pydantic import BaseModel, ConfigDict, computed_field, Field

from src.models.cart import CartStatus


class ProductInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float
    quantity: int
    is_active: bool


class CartProductsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: "ProductInfo"

    your_price: float | None = Field(None, alias="product_price")
    product_quantity: int
    amount: int | None = Field(None, alias="product_amount")

    @computed_field
    def available(self) -> str:
        if self.product.quantity == 0 or not self.product.is_active:
            return "Out of stock"
        elif self.product_quantity < self.product.quantity:
            return "In stock"
        else:
            return f"{self.product.quantity} available"

    @computed_field
    def product_price(self) -> float:
        if self.your_price is not None:
            return self.your_price
        return self.product.price

    @computed_field
    def product_amount(self) -> float:
        # Логика 2: если сумма в корзине None, вычисляем (цена * кол-во)
        if self.amount is not None:
            return self.amount
        return self.product_price * self.product_quantity


class CartOut(BaseModel):

    id: int
    user_id: int
    status: CartStatus

    products: List[CartProductsOut]

    @computed_field
    def amount(self) -> float:
        return sum(item.product_amount for item in self.products if item.product_amount)


class ProductAdd(BaseModel):

    cart_id: int | None = Field(None, alias="cart_id")
    product_id: int
    product_quantity: int
