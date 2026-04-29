# routers/user.py
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.config.database import db_handler
from src.config.settings import get_settings
from src.crud.cart import add_user_cart
from src.crud.user import (
    get_user_by_id,
    get_users_paginated,
    get_role_by_name,
    add_role_to_user,
    add_new_user
)
from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker
from src.models.user import User
from src.schemas.user import UserInfo, UserRegister, UsersPaginatedOut
from src.utils.pagination import CursorHandler
from src.utils.security import PasswordHandler

debug_logger = logging.getLogger("debug")

exception_user_exist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email or phone already exists"
)
exception_register_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Не получается зарегистрировать пользователя",
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserInfo, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserRegister,
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для создания нового пользователя.
    Валидация данных производится в объекте pydantic.
    Создание нового пользователя, корзины и добавление роли
    для нового пользователя производится в единой транзакции.
    Доступен для всех пользователей
    """

    user_data = user.model_dump(exclude={"confirm_password"})
    user_data["hashed_password"] = PasswordHandler.get_password_hash(user_data.pop("password"))
    user_data["is_active"] = True

    try:
        try:
            new_user = await add_new_user(user=user_data, session=session)
        except IntegrityError:
            raise exception_user_exist

        await add_user_cart(new_user, session=session)
        try:
            role = await get_role_by_name(name="Customer", session=session)
            await add_role_to_user(user=new_user, role=role, session=session)
        except Exception:
            pass

        await session.commit()
        await session.refresh(new_user)

    except HTTPException as http_ex:
        await session.rollback()
        raise http_ex

    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create user failed: {e.args} ---")
        raise exception_register_error

    debug_logger.info(f"Successfully registered user {new_user.email}")
    return new_user


@router.get("/", response_model=UsersPaginatedOut)
async def get_users(
    # current_user: Annotated[User, Depends(PermissionChecker(["users:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
    limit: int = Query(**get_settings().pagination.model_dump()),
    name_query: Optional[str] = None,
    cursor: Optional[str] = Query(None, description="Format: name::id"),
):
    """
    Эндпоинт для получения отсортированного списка пользователей.
    Включает пагинацию (с возможностью задания лимита на стороне пользователя),
    возможность сортировки по полю full_name

    Доступен для пользователей с разрешением "users:view"
    """

    # Преобразовываем и проверяем курсор курсором
    cursor_data = await CursorHandler.get_cursor_data(cursor) if cursor else None

    users_list = await get_users_paginated(
        session=session, limit=limit, name_query=name_query, cursor_data=cursor_data
    )

    next_cursor = await CursorHandler.get_next_cursor_user(users_list[-1]) if len(users_list) == limit else None

    return UsersPaginatedOut(items=users_list, next_cursor=next_cursor)


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: Annotated[User, Depends(AuthUserDependencies.get_current_user)],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для просмотра информации о текущем пользователе
    Доступен для пользователей с разрешением "users:view"
    """

    return current_user


@router.get("/{user_id}", response_model=UserInfo)
async def get_user_info(
    user_id: int,
    current_user: Annotated[User, Depends(PermissionChecker(["users:view"]))],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для просмотра информации о пользователе
    Доступен для пользователей с разрешением "users:view"
    """

    user = await get_user_by_id(session=session, user_id=user_id)
    return user
