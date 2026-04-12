from datetime import datetime
from typing import Annotated, List

from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Product(Base):
    """
    Модель Товары для сохранения данных
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now())
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))

    # Обратные связи
    carts: Mapped[List["CartProducts"]] = relationship(
        back_populates="products"
    )

    def __str__(self):
        return f"{self.id} - {self.name} - {self.price} - {self.quantity}"
