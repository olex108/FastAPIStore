from enum import Enum

from pydantic import BaseModel


class PaginationSettings(BaseModel):
    default: int = 10
    gt: int = 0
    le: int = 50


class SortOptions(str, Enum):
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
