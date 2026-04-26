# routers/user.py
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import db_handler

from src.models.user import User
from src.crud.user import create_new_user, get_all_users, get_user_by_id
from src.crud.cart import create_cart
from src.schemas.user import UserInfo, UserRegister, UserUpdate
from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker
from sqlalchemy.exc import IntegrityError
from src.utils.security import PasswordHandler

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserInfo, status_code=status.HTTP_201_CREATED)
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

    user_data = user.model_dump(exclude={"confirm_password"})
    user_data["hashed_password"] = PasswordHandler.get_password_hash(user_data.pop("password"))
    # Убрать поле при добавлении системы верификации пользователя !!!!!!!!!!!!
    user_data["is_active"] = True

    new_user = await create_new_user(user=user_data, session=session)
    user_cart = await create_cart(new_user, session=session)

    return new_user


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


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
        current_user: Annotated[User, Depends(AuthUserDependencies.get_current_user)],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)]
):
    """
    Эндпоинт для просмотра информации о текущем пользователе
    """

    return current_user


@router.get("/{user_id}", response_model=UserInfo)
async def get_current_user_info(
        user_id: int,
        current_user: Annotated[User, Depends(PermissionChecker(["users:view"]))],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)]
):
    """
    Эндпоинт для просмотра информации о текущем пользователе
    """
    user = await get_user_by_id(session=session, user_id=user_id)

    return user
