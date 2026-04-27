# routers/cart.py
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.crud.cart import (add_product_to_cart, add_products_list_to_cart, clear_cart_products,
                           delete_product_from_cart, get_user_cart)
from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import OwnerOrPermissionChecker
from src.models.cart import CartStatus
from src.models.user import User
from src.schemas.cart import CartOut, ProductAdd

router = APIRouter(prefix="/cart", tags=["Carts"])

exception_400_add_prod = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request of added product")
exception_400_del_prod = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request of delete product")
exception_500_get_cart = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can`t get cart data")
exception_400_cart_in_order = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Cart in order. Create new cart"
)


@router.get("/me", response_model=CartOut)
async def get_current_user_cart(
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для получения Корзины текущего пользователя
    """

    try:
        user_cart = await get_user_cart(user_id=current_user.id, session=session)
        return user_cart
    except Exception:
        raise exception_500_get_cart


@router.get("/{user_id}", response_model=CartOut)
async def get_cart(
    user_id: int,
    current_user: Annotated[
        User,
        Depends(
            OwnerOrPermissionChecker(
                [
                    "carts:view",
                ]
            )
        ),
    ],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для получения Корзины пользователя по user_id
    Доступный при наличии разрешения "carts:view" или для активного собственника корзины
    """

    try:
        user_cart = await get_user_cart(user_id=user_id, session=session)
        return user_cart
    except Exception:
        raise exception_500_get_cart


@router.post("/me/add_product", response_model=CartOut)
async def add_product(
    product: ProductAdd,
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для добавления продукта в корзину текущего пользователя

    Эндпоинт можно использовать для изменения значения продукта
    """

    # Проверка статуса корзины
    if current_user.cart.status != CartStatus.CURRENT:
        raise exception_400_cart_in_order

    try:
        await add_product_to_cart(cart_id=current_user.cart.id, product=product, session=session)
    except Exception:
        raise exception_400_add_prod

    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart


@router.post("/{user_id}/add_product", response_model=CartOut)
async def add_user_product(
    user_id: int,
    product: ProductAdd,
    current_user: Annotated[
        User,
        Depends(
            OwnerOrPermissionChecker(
                [
                    "carts:update",
                ]
            )
        ),
    ],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для добавления продукта в корзину пользователя по user_id
    Доступный при наличии разрешения "carts:update" или для активного собственника корзины

    Эндпоинт можно использовать для изменения значения продукта
    """

    # Получение cart id
    try:
        user_cart = await get_user_cart(user_id=user_id, session=session)
        if user_cart.status != CartStatus.CURRENT:
            raise exception_400_cart_in_order
    except Exception:
        raise exception_400_add_prod

    # Добавляем продукт в корзину
    try:
        await add_product_to_cart(cart_id=user_cart.id, product=product, session=session)
    except Exception:
        raise exception_400_add_prod

    try:
        cart = await get_user_cart(user_id=user_id, session=session)
    except Exception:
        raise exception_400_add_prod

    return cart


@router.post("/me/add_products", response_model=CartOut)
async def add_products_list(
    products_list: List[ProductAdd],
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для добавления списка товаров в корзину

    Добавляет товары по id в указанном количестве,
    в случае если товар в корзине суммирует количество товаров в корзине и добавленных товаров
    """

    # Проверка статуса корзины
    if current_user.cart.status != CartStatus.CURRENT:
        raise exception_400_cart_in_order

    try:
        await add_products_list_to_cart(cart_id=current_user.cart.id, products_list=products_list, session=session)
    except Exception:
        raise exception_400_add_prod
    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart


@router.delete("/me/{product_id}", response_model=CartOut)
async def delete_my_product(
    product_id: int,
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для удаления продукта из корзины текущего пользователя
    """

    # Проверка статуса корзины
    if current_user.cart.status != CartStatus.CURRENT:
        raise exception_400_cart_in_order

    try:
        await delete_product_from_cart(product_id=product_id, cart_id=current_user.cart.id, session=session)
    except Exception:
        raise exception_400_del_prod

    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart


@router.delete("/{user_id}/{product_id}", response_model=CartOut)
async def delete_user_product(
    user_id: int,
    product_id: int,
    current_user: Annotated[
        User,
        Depends(
            OwnerOrPermissionChecker(
                [
                    "carts:update",
                ]
            )
        ),
    ],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для удаления продукта в из корзины пользователя user_id
    Доступный при наличии разрешения "carts:update" или для активного собственника корзины
    """

    # Получение cart id
    try:
        user_cart = await get_user_cart(user_id=user_id, session=session)
        if user_cart.status != CartStatus.CURRENT:
            raise exception_400_cart_in_order
    except Exception:
        raise exception_400_add_prod

    try:
        await delete_product_from_cart(product_id=product_id, cart_id=user_cart.id, session=session)
    except Exception:
        raise exception_400_del_prod

    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart


@router.delete("/me/clear", response_model=CartOut)
async def clear_cart(
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для очистки корзины пользователя
    """

    # Проверка статуса корзины
    if current_user.cart.status != CartStatus.CURRENT:
        raise exception_400_cart_in_order

    try:
        await clear_cart_products(cart_id=current_user.cart.id, session=session)
    except Exception:
        raise exception_400_del_prod
    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart
