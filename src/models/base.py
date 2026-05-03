# from datetime import datetime
# from typing import Annotated
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


# class ModelsAnnotation:
#     """Кастомные настройки аннотации полей в моделях"""
#
#     created_at = Annotated[datetime, mapped_column(server_default=datetime.now())]
#     updated_at = Annotated[datetime, mapped_column(server_default=datetime.now(), onupdate=datetime.now())]


# Создание базового класса для наследования моделями
class Base(DeclarativeBase):
    """Базовый класс для наследования моделями"""

    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

# Импортируем модели для инициализации при миграциях
# from .auth import RefreshSession
# from .cart import Cart, CartProducts
# from .product import Product
# from .user import Role, RoleUsers, User, Permission, RolePermissions
