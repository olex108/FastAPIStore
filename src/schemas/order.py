from datetime import datetime

from pydantic import BaseModel

from src.models.order import OrdersStatus


class ContactOut(BaseModel):
    model_config = {"from_attributes": True}

    inn: int
    name: str
    email: str
    address: str
    phone: int


class OrderOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    order_at: datetime
    order_amount: int
    status: OrdersStatus
