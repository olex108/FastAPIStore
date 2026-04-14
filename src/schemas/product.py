from pydantic import BaseModel

from datetime import datetime


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


class ProductOut(Product):
    id: int

    model_config = {"from_attributes": True}
