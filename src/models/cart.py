# models/cart.py
from typing import List

from sqlalchemy import ForeignKey, null, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from .base import Base
from .product import Product

import enum


class CartStatus(str, enum.Enum):
    """Клас Enum для вариантов статуса Корзины"""

    CURRENT = "current"
    IN_PROGRESS = "processing"
    COMPLETED = "completed"


class Cart(Base):
    """
    Модель Корзина для хранения данных о заказе пользователя
    user_id: уникальное поле так как в одного пользователя должна быть одна корзина
    user: связь с пользователем
    products: список товаров в корзине
    """

    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[CartStatus] = mapped_column(default=CartStatus.CURRENT)
    order_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    order_amount: Mapped[int] = mapped_column(nullable=True, default=None)

    # Обратные связи
    user: Mapped["User"] = relationship(back_populates="cart")
    products: Mapped[List["CartProducts"]] = relationship(
        back_populates="cart",
    )

    __table_args__ = (
        Index(
            "idx_user_current_cart_unique",
            user_id,
            postgresql_where=(status == CartStatus.CURRENT.value),
            unique=True
        ),
    )

    def __str__(self):
        return f"{self.id} - {self.user_id} - {self.status}"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, uerr_id={self.user_id}, status={self.status})"


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
    product_price: Mapped[float] = mapped_column(nullable=True, default=None)
    product_quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    product_amount: Mapped[int] = mapped_column(nullable=True, default=None)

    # Обратные связи
    cart: Mapped["Cart"] = relationship(
        back_populates="products",
    )
    product: Mapped["Product"] = relationship(
        back_populates="carts",
    )

    __table_args__ = (
        Index(
            "idx_cart_product_unique",
            cart_id,
            product_id,
            unique=True
        ),
    )


class CartHistory(Base):
    """
    !!!!!! В разработке - не добавлен в __init__ для исключения миграций !!!!!!!!!!

    Модель Истории Корзин для хранения данных о выполненных заказах пользователей
    user_id: уникальное поле так как в одного пользователя должна быть одна корзина
    user: связь с пользователем
    products: список товаров в корзине
    """

    __tablename__ = "carts_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    order_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    order_amount: Mapped[int] = mapped_column(nullable=True, default=None)

    # Обратные связи
    # user: Mapped["User"] = relationship(back_populates="cart")
    # products: Mapped[List["CartProducts"]] = relationship(
    #     back_populates="cart",
    # )

    # __table_args__ = (
    #     Index(
    #         "idx_user_current_cart_unique",
    #         user_id,
    #         postgresql_where=(status == CartStatus.CURRENT.value),
    #         unique=True
    #     ),
    # )

    def __str__(self):
        return f"{self.id} - {self.user_id} - {self.status}"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, uerr_id={self.user_id}, status={self.status})"
