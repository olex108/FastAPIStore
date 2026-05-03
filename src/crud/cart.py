import logging
from datetime import datetime
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.cart import Cart, CartProducts, CartStatus
from src.models.user import User
from src.schemas.cart import ProductAdd

debug_logger = logging.getLogger("debug")


async def create_user_cart(user: User, session: AsyncSession) -> None:
    try:
        new_cart = Cart(user_id=user.id)
        session.add(new_cart)
        await session.commit()
        debug_logger.info("--- Created new cart ---")

    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create cart failed: {e.args} ---")
        raise e


async def add_user_cart(user: User, session: AsyncSession) -> Cart:

    new_cart = Cart(user_id=user.id)
    session.add(new_cart)
    await session.flush()
    return new_cart


async def update_ordered_cart(cart: Cart, order_at: datetime, order_amount: float, session: AsyncSession) -> None:
    cart.order_at = order_at
    cart.order_amount = int(order_amount)
    cart.status = CartStatus.IN_PROGRESS
    try:
        await session.commit()
        debug_logger.info("--- Updated cart ---")
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Update cart failed: {e.args} ---")


async def get_cart_by_user_id(user_id: int, session: AsyncSession) -> Cart:
    try:
        query = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.products).selectinload(CartProducts.product))
        )
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create cart failed: {e.args} ---")
        raise e


async def get_cart_id_by_user_id(user_id: id, session: AsyncSession) -> int | None:
    """
    Запрос на получение корзины по user_id
    """

    query = select(Cart.id).where(Cart.user_id == user_id)
    cart_id = (await session.execute(query)).scalar_one_or_none()
    return cart_id


async def add_product_to_cart(cart_id: int, product: ProductAdd, session: AsyncSession) -> None:
    """
    Функция для добавления продукта в корзину.
    Принимает продукт
    В случае наличия продукта в корзине (проверка по product_id) заменяет старое значение на новое
    """

    new_product = {
        "cart_id": cart_id,
        "product_id": product.product_id,
        "product_quantity": product.product_quantity,
    }
    query = insert(CartProducts).values(new_product)

    upsert_stmt = query.on_conflict_do_update(
        index_elements=["cart_id", "product_id"], set_={"product_quantity": query.excluded.product_quantity}
    )

    try:
        await session.execute(upsert_stmt)
        await session.commit()
        debug_logger.info(f"Add product {product.product_id}")
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Add product failed: {e.args} ---")
        raise e


async def add_products_list_to_cart(cart_id: int, products_list: List[ProductAdd], session: AsyncSession) -> None:
    """
    Функция для добавления списка продуктов в корзину.
    Принимает список продуктов
    В случае наличия продукта в корзине (проверка по product_id) производится суммирование старого и нового значений
    """

    new_products = [
        {
            "cart_id": cart_id,
            "product_id": product.product_id,
            "product_quantity": product.product_quantity,
        }
        for product in products_list
    ]

    query = insert(CartProducts).values(new_products)

    upsert_query = query.on_conflict_do_update(
        index_elements=["cart_id", "product_id"],
        set_={"product_quantity": CartProducts.product_quantity + query.excluded.product_quantity},
    )

    try:
        await session.execute(upsert_query)
        await session.commit()
        debug_logger.info(f"Add products list with {len(products_list)} products")
    except IntegrityError as e:
        await session.rollback()
        debug_logger.error(f"--- Add product failed: {e.args} ---")
        raise e


async def delete_product_from_cart(product_id: int, cart_id: int, session: AsyncSession) -> None:
    query = delete(CartProducts).where(CartProducts.cart_id == cart_id, CartProducts.product_id == product_id)

    try:
        await session.execute(query)
        await session.commit()
        debug_logger.info(f"Delete product {product_id} from cart {cart_id}")
    except IntegrityError as e:
        await session.rollback()
        debug_logger.error(f"--- Delete product failed: {e.args} ---")
        raise e


async def clear_cart_products(cart_id: int, session: AsyncSession) -> None:
    query = (delete(CartProducts)).where(
        CartProducts.cart_id == cart_id,
    )

    try:
        await session.execute(query)
        await session.commit()
        debug_logger.info(f"Clear cart products {cart_id}")

    except IntegrityError as e:
        await session.rollback()
        debug_logger.error(f"--- Clear cart products failed: {e.args} ---")
        raise e


async def default_user_cart_settings(cart_id: int, session: AsyncSession) -> Cart | None:

    cart = await session.get(Cart, cart_id)
    if not cart:
        debug_logger.warning(f"--- Cart with id {cart_id} not found ---")
        return None

    cart.status = CartStatus.CURRENT
    cart.order_amount = None
    cart.order_at = None

    try:
        await session.commit()
        await session.refresh(cart)
    except Exception as e:
        debug_logger.error(f"--- Default cart failed: {e.args} ---")
        return None

    return cart
