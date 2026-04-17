import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config.database import db_handler
from src.models.user import User
from src.models.cart import Cart, CartProducts
from src.models.product import Product


debug_logger = logging.getLogger("debug")


async def create_cart(user: User, session: Annotated[AsyncSession, Depends(db_handler.session_getter)]):
    try:
        new_cart = Cart(user_id=user.id)
        session.add(new_cart)
        await session.commit()

    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create cat failed: {e} ---")
        raise e

async def get_user_cart(user_id: int, session: Annotated[AsyncSession, Depends(db_handler.session_getter)]):
    try:
        query = (
            select(Cart).where(
                    Cart.user_id == user_id
                )
            .options(
                selectinload(Cart.products).selectinload(CartProducts.product_id)
            )
        )
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create cat failed: {e} ---")
        raise e