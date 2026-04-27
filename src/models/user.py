# models/user.py
from typing import List

from sqlalchemy import ForeignKey, String
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
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False, server_default="false")

    # Обратные связи
    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False)
    roles: Mapped[List["Role"]] = relationship(
        back_populates="users",
        secondary="role_users",
    )

    def __str__(self):
        return f"{self.id} - {self.full_name} - {self.is_superuser} - {self.is_active}"


class Role(Base):
    """
    Модель Группы
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Обратные связи
    users: Mapped[List["User"]] = relationship(
        back_populates="roles",
        secondary="role_users",
    )
    permissions: Mapped[List["Permission"]] = relationship(
        back_populates="roles",
        secondary="role_permissions",
    )

    def __str__(self):
        return f"{self.id} - {self.name}"


class Permission(Base):
    """
    Модель Разрешения
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Обратные связи
    roles: Mapped[List["Role"]] = relationship(
        back_populates="permissions",
        secondary="role_permissions",
    )

    def __str__(self):
        return f"{self.id} - {self.name}"


class RolePermissions(Base):
    """Модель для связи между Группой и Разрешением any_to_many"""

    __tablename__ = "role_permissions"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class RoleUsers(Base):
    """Модель для связи между Пользователем и Группой any_to_many"""

    __tablename__ = "role_users"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
