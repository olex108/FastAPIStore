#models/cart.py
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .product import Product


class Cart(Base):
    """
    Модель Корзина для хранения данных о заказе пользователя
    user_id: уникальное поле так как в одного пользователя должна быть одна корзина
    user: связь с пользователем
    products: список товаров в корзине
    """

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Обратные связи
    user: Mapped["User"] = relationship(back_populates="cart")
    products: Mapped[List["CartProducts"]] = relationship(
        back_populates="carts",
    )

    def __str__(self):
        return f"{self.id} - {self.user_id}"


class CartProducts(Base):
    """
    Модель ТоварыКорзины для хранения данных о количестве товаров в корзине и связи many_to_many
    cart_id: ссылка на корзину
    product_id: ссылка на продукт
    """

    __tablename__ = "cart_products"

    # ссылки для связи моделей
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)

    # дополнительное поле
    product_quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    # Обратные связи
    carts: Mapped[List["Cart"]] = relationship(
        back_populates="products",
    )
    products: Mapped[List["Product"]] = relationship(
        back_populates="carts",
    )
