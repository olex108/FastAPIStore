# models/user.py
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """
    Модель Пользователя
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Обратные связи
    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False)
    groups: Mapped[List["Group"]] = relationship(
        back_populates="users",
        secondary="group_users",
    )

    def __str__(self):
        return f"{self.id} - {self.full_name} - {self.phone}"


class Group(Base):
    """
    Модель Группы
    """
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Обратные связи
    users: Mapped[List["User"]] = relationship(
        back_populates="groups",
        secondary="group_users",
    )

    def __str__(self):
        return f"{self.id} - {self.name}"


class GroupUsers(Base):
    """Модель для связи между Пользователем и Группой any_to_many"""

    __tablename__ = "group_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
