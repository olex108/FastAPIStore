# routers/user.py
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import db_handler

from src.models.user import User
from src.crud.user import create_new_user, get_all_users
from src.crud.cart import create_cart
from src.schemas.user import UserInfo, UserRegister, UserUpdate
from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserInfo)
async def register_user(
    user: UserRegister,
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для создания нового пользователя.
    Доступен для всех пользователей
    Валидация данных производится в объекте pydantic.
    Создается новый пользователь в БД и корзина для нового пользователя
    """

    try:
        print("Stage", 1)
        new_user = await create_new_user(user=user, session=session)
        print("Stage", 2)
        user_cart = await create_cart(new_user, session=session)
        print("Stage", 3)
        return new_user
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не получается зарегистрировать пользователя",
        )


@router.get("/", response_model=List[UserInfo])
async def get_users(
    current_user: Annotated[User, Depends(PermissionChecker(["users:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)]
):
    """
    Эндпоинт для просмотра списка пользователей
    Доступен для пользователей с разрешением "users:view"
    """

    users = await get_all_users(session=session)
    return users


@router.get("/me", response_model=UserUpdate)
async def get_current_user_info(
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_user)]
):
    """
    Эндпоинт для просмотра информации о текущем пользователе
    """

    return current_user
