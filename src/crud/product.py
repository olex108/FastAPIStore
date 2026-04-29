import logging
from typing import Optional, Sequence

from sqlalchemy import and_, asc, desc, or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.pagination import SortOptions
from src.models.product import Product
from src.schemas.product import CreateProduct

debug_logger = logging.getLogger("debug")


async def create_new_product(new_product: CreateProduct, session: AsyncSession) -> Product:
    product = Product(**new_product.model_dump())
    session.add(product)
    try:
        await session.commit()
        await session.refresh(product)
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create product failed: {e.args} ---")
        raise e
    return product


async def get_all_products(session: AsyncSession) -> Sequence[Product]:
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_active_products(session: AsyncSession) -> Sequence[Product]:
    query = select(Product).where(Product.is_active)
    result = await session.execute(query)
    return result.scalars().all()


async def get_products_paginated(
    session: AsyncSession,
    limit: int,
    sort_by: SortOptions,
    name_query: Optional[str] = None,
    cursor_data: Optional[tuple] = None,  # (last_val, last_id)
) -> Sequence[Product]:
    """
    Запрос на получение отфильтрованного и отсортированного списка товаров
    """

    query = select(Product)

    # Применяем фильтрацию по имени
    if name_query:
        query = query.where(Product.name.ilike(f"%{name_query}%"))

    # Применяем фильтрацию курсором
    if cursor_data:
        last_val, last_id = cursor_data
        if sort_by == SortOptions.name_asc:
            query = query.where(tuple_(Product.name, Product.id) > (last_val, last_id))
        elif sort_by == SortOptions.price_asc:
            query = query.where(tuple_(Product.price, Product.id) > (int(last_val), last_id))
        elif sort_by == SortOptions.price_desc:
            query = query.where(
                or_(Product.price < int(last_val), and_(Product.price == int(last_val), Product.id > last_id))
            )

    # Применяем сортировку
    if sort_by == SortOptions.name_asc:
        query = query.order_by(Product.name.asc(), Product.id.asc())
    elif sort_by == SortOptions.price_desc:
        query = query.order_by(Product.price.desc(), Product.id.asc())
    else:
        query = query.order_by(Product.price.asc(), Product.id.asc())
    # Применяем лимит
    query = query.where(Product.is_active).limit(limit)
    result = await session.execute(query)

    return result.scalars().all()


async def get_product_by_id(product_id: int, session: AsyncSession) -> Product | None:
    query = select(Product).where(Product.id == product_id)
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def update_product_by_id(product: CreateProduct, product_id: int, session: AsyncSession) -> Product | None:
    db_product = await session.get(Product, product_id)
    if db_product is None:
        return None
    db_product.name = product.name
    db_product.quantity = product.quantity
    db_product.price = product.price
    db_product.is_active = product.is_active
    try:
        await session.commit()
        await session.refresh(db_product)
        return db_product
    except Exception as e:
        debug_logger.error(f"--- Update product failed: {e.args} ---")
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
        debug_logger.error(f"--- Delete product failed: {e.args} ---")
        return None
