# routers/cart.py
from fastapi import APIRouter
from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.crud.cart import get_user_cart, add_product_to_cart, add_products_list_to_cart
from src.dependencies.permissions import PermissionChecker, OwnerOrPermissionChecker
from src.config.database import db_handler

from src.schemas.cart import CartOut, ProductAdd

router = APIRouter(
    prefix="/cart",
    tags=["Carts"]
)


exception_400_add_prod = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request of added product")
exception_500_get_cart = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can`t get cart data")


@router.get("/me", response_model=CartOut)
async def get_current_user_cart(
        current_user: Annotated[User, Depends(OwnerOrPermissionChecker())],
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
        current_user: Annotated[User, Depends(OwnerOrPermissionChecker(["carts:view",]))],
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
        current_user: Annotated[User, Depends(OwnerOrPermissionChecker())],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для добавления продукта в корзину текущего пользователя
    """

    try:
        await add_product_to_cart(product=product,  session=session)
    except Exception:
        raise exception_400_add_prod

    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart


@router.post("/{user_id}/add_product", response_model=CartOut)
async def add_product(
        user_id: int,
        product: ProductAdd,
        current_user: Annotated[User, Depends(PermissionChecker(["carts:update"]))],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для добавления продукта в корзину пользователя по user_id
    Доступный при наличии разрешения "carts:update"
    """

    try:
        await add_product_to_cart(product=product,  session=session)
    except Exception:
        raise exception_400_add_prod
    try:
        cart = await get_user_cart(user_id=user_id, session=session)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Can`t get cart data",
        )

    return cart


@router.post("/me/add_products", response_model=CartOut)
async def add_products(
        products_list: List[ProductAdd],
        current_user: Annotated[User, Depends(OwnerOrPermissionChecker())],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):

    try:
        await add_products_list_to_cart(products_list=products_list, session=session)
    except Exception:
        raise exception_400_add_prod
    try:
        cart = await get_user_cart(user_id=current_user.id, session=session)
    except Exception:
        raise exception_500_get_cart

    return cart
