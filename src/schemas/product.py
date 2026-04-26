from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: int
    quantity: int
    create_at: datetime
    update_at: datetime
    is_active: bool


class CreateProduct(BaseModel):
    name: str
    price: int
    quantity: int
    is_active: bool = True


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    quantity: int
    is_active: bool

    model_config = {"from_attributes": True}


class ProductPaginationOut(BaseModel):
    items: List[ProductOut]
    next_cursor: Optional[str]