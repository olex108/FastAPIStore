import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.cart import CartStatus


class Contacts(Base):
    __tablename__ = "contacts"

    inn: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    phone: Mapped[int] = mapped_column()


class OrdersStatus(str, enum.Enum):
    """Клас Enum для вариантов статуса Истории заказов"""

    IN_PROGRESS = "processing"
    COMPLETED = "completed"
    CANCELED = "canceled"


class Order(Base):
    """
    !!!!!! В разработке - не добавлен в __init__ для исключения миграций !!!!!!!!!!

    Модель Истории Корзин для хранения данных о выполненных заказах пользователей
    user_id: уникальное поле так как в одного пользователя должна быть одна корзина
    user: связь с пользователем
    products: список товаров в корзине
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    order_at: Mapped[datetime] = mapped_column()
    order_amount: Mapped[int] = mapped_column()
    status: Mapped[CartStatus] = mapped_column(
        SQLEnum(OrdersStatus, name="orderstatus"),  # Явно указываем имя типа для Postgres
        default=CartStatus.CURRENT,
        nullable=False,
    )
    receipt_url: Mapped[str] = mapped_column(nullable=False)

    # Обратные связи
    user: Mapped["User"] = relationship(back_populates="orders")

    def __str__(self):
        return f"{self.id} - {self.user_id} - {self.status} - {self.order_at} - {self.order_amount}"

    def __repr__(self):
        return f"{self.id} - {self.user_id} - {self.status} - {self.order_at} - {self.order_amount}"
