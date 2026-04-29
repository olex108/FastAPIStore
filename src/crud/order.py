import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import Contacts, Order, OrdersStatus
from src.schemas.cart import CartOut

debug_logger = logging.getLogger("debug")


async def get_contacts_data(session: AsyncSession) -> Contacts | None:

    query = select(Contacts).limit(1)
    result = await session.execute(query)

    return result.scalars().first()


async def create_new_order(user_cart: CartOut, receipt_url: str, session: AsyncSession) -> Order | None:

    new_order = Order(
        user_id=user_cart.user_id,
        order_at=user_cart.order_at,
        order_amount=user_cart.amount,
        status=OrdersStatus.IN_PROGRESS,
        receipt_url=receipt_url,
    )
    session.add(new_order)
    try:
        await session.commit()
        await session.refresh(new_order)
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create order failed: {e.args} ---")

    debug_logger.info(f"--- Order created successfully: ID {new_order.id} ---")
    return new_order
