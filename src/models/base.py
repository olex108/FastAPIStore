from typing import Annotated
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column


class ModelsAnnotated:
    created_at = Annotated[datetime, mapped_column(server_default=datetime.now())]
    updated_at = Annotated[datetime, mapped_column(server_default=datetime.now(), onupdate=datetime.now())]


# Создание базового класса
class Base(DeclarativeBase):
    pass


from .product import Product
from .user import User
from .cart import Cart
