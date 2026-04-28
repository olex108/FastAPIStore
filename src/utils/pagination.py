from enum import Enum
from typing import Optional
from fastapi import HTTPException

from src.config.pagination import SortOptions
from src.models import Product, User


class CursorHandler:

    @staticmethod
    async def get_cursor_data(cursor: Optional[str]) -> Optional[tuple[int|str, int]]:
        try:
            val, last_id = cursor.rsplit("::", 1)
            cursor_data = (val, int(last_id))
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Incorrect cursor format")

        return cursor_data

    @staticmethod
    async def get_next_cursor_product(last_item: Product, sort_by: SortOptions) -> Optional[str | None]:
        try:
            val = last_item.name if sort_by == SortOptions.name_asc else last_item.price
        except (ValueError, IndexError):
            return None

        return f"{val}::{last_item.id}"

    @staticmethod
    async def get_next_cursor_user(
            last_item: User,
            # sort_by: SortOptions
    ) -> Optional[str | None]:

        try:
            val = last_item.full_name
        except (ValueError, IndexError):
            return None

        return f"{val}::{last_item.id}"
