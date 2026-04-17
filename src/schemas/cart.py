from pydantic import BaseModel


class CartOut(BaseModel):
    id: int
    products: List[]