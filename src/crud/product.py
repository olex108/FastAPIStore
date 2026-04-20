import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import Product
from src.schemas.product import CreateProduct

debug_logger = logging.getLogger("debug")


async def create_product(new_product: CreateProduct, session: AsyncSession) -> Product:
    product = Product(**new_product.model_dump())
    session.add(product)
    try:
        await session.commit()
        await session.refresh(product)
    except Exception as e:
        await session.rollback()
        debug_logger.debug(f"--- Create product failed: {e} ---")
        raise e
    return product


async def get_all_products(session: AsyncSession) -> Sequence[Product]:
    query = select(Product).order_by(Product.id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_product_by_id(product_id: int, session: AsyncSession) -> Product | None:
    query = select(Product).where(Product.id == product_id)
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def update_product_by_id(product: CreateProduct, product_id: int, session: AsyncSession) -> Product | None:
    db_product = await session.get(Product, product_id)
    if db_product is None:
        return db_product
    try:
        db_product.name = product.name
        db_product.quantity = product.quantity
        db_product.price = product.price
        db_product.is_active = product.is_active
        await session.commit()
        await session.refresh(db_product)
        return db_product
    except Exception as e:
        debug_logger.debug(f"--- Update product failed: {e} ---")
        return None


async def delete_product_by_id(
    product_id: int,
    session: AsyncSession,
) -> Product | None:

    db_product = await session.get(Product, product_id)
    if db_product is None:
        return db_product
    try:
        await session.delete(db_product)
        await session.commit()
        return db_product
    except Exception as e:
        debug_logger.debug(f"--- Delete product failed: {e} ---")
        return None
