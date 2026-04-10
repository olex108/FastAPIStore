from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from typing import Annotated
from datetime import datetime
from sqlalchemy import func, text


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] =  mapped_column(server_default=func.now(), onupdate=datetime.now())
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))

    def __str__(self):
        return f"{self.name} - {self.price} - {self.is_active}"
