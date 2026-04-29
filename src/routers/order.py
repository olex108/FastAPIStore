from datetime import datetime
from datetime import date
from typing import Annotated

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.models.cart import CartStatus
from src.models.order import OrdersStatus
from src.schemas.cart import CartOut
from src.schemas.order import ContactOut, OrderOut
from src.crud.order import get_contacts_data, create_new_order
from src.dependencies.auth import AuthUserDependencies
from src.config.database import db_handler
from src.crud.cart import get_cart_by_user_id, update_ordered_cart
from src.crud.user import  get_user_by_id
from src.services.excel_receipt_generator import generate_receipt_excel
from src.services.mailing import send_email_task
from src.config.settings import get_settings

settings = get_settings()


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# @router.get("/contacts", response_model=ContactOut)
# async def get_contacts(
#     session: AsyncSession,
# ):
#     return await get_contacts_data(session=session)


@router.post("/make_order", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def make_order(
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)]
):

    # получаем данные из базы данных
    db_cart = await get_cart_by_user_id(user_id=current_user.id, session=session)
    if db_cart.status != CartStatus.CURRENT:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Cart is ordered, create new cart first"
        )
    user_data = await get_user_by_id(session=session, user_id=current_user.id)
    contact_data = await get_contacts_data(session=session)
    # Преобразовываем user_cart из orm модели в pydantic и добавляем время заказа
    pydantic_cart = CartOut.model_validate(db_cart)
    pydantic_cart.order_at = datetime.now()
    # Создаем excel чек и получаем путь к файлу
    receipt_url = generate_receipt_excel(pydantic_cart, contact_data, user_data)
    # Сохраняем заказ и обновляем корзину в БД
    order = await create_new_order(user_cart=pydantic_cart, receipt_url=receipt_url, session=session)
    if order is not None:
        await update_ordered_cart(cart=db_cart, order_at=pydantic_cart.order_at, order_amount=pydantic_cart.amount, session=session)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    # 3. Отправляем в Taskiq
    full_file_path = settings.BASE_DIR / receipt_url
    print("Path to file -----------", full_file_path)

    with open(full_file_path, "rb") as f:
        file_content = f.read()

    await send_email_task.kiq(
        subject=f"Ваш чек по заказу №{pydantic_cart.id}",
        recipient=current_user.email,
        body="Благодарим за заказ! Ваш чек во вложении.",
        file_path=str(full_file_path)
    )

    return order
