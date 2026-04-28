# routers/user.py
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.config.settings import get_settings
from src.crud.cart import create_cart
from src.crud.user import add_role_to_user, create_new_user, get_user_by_id, get_users_paginated, get_role_by_name
from src.dependencies.auth import AuthUserDependencies
from src.dependencies.permissions import PermissionChecker
from src.models.user import User
from src.schemas.user import UserInfo, UserRegister, UsersPaginatedOut
from src.utils.pagination import CursorHandler
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
    try:
        # Создаем корзину и добавляем роль для нового пользователя
        await create_cart(new_user, session=session)
        role = await get_role_by_name(name="Customer", session=session)
        await add_role_to_user(user=new_user, role=role, session=session)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
