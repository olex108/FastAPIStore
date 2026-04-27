import logging
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import or_, select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import Role, RoleUsers, User

debug_logger = logging.getLogger("debug")


exception_user_exist = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email or phone already exists"
)
exception_register_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Не получается зарегистрировать пользователя",
)


async def create_new_user(user: dict, session: AsyncSession) -> User:

    new_user = User(**user)
    session.add(new_user)

    try:
        await session.commit()
        await session.refresh(new_user)
        debug_logger.info(f"Created new user {new_user}")
    except IntegrityError as e:
        await session.rollback()
        debug_logger.warning(f"--- Create user failed (IntegrityError): {e.args} ---")
        raise exception_user_exist
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create user failed: {e.args} ---")
        raise exception_register_error

    return new_user


async def add_role_to_user(user: User, role: str, session: AsyncSession) -> None:
    customer_role = select(Role).where(Role.name == role)
    customer_role = (await session.execute(customer_role)).scalar_one_or_none()
    if customer_role:
        new_role_user = RoleUsers(role_id=role, user_id=user.id)
        session.add(new_role_user)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            debug_logger.error(f"--- Add user to role: {role} failed: {e.args} ---")


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    query = select(User).order_by(User.id)
    result = await session.scalars(query)
    return result.all()


async def get_users_paginated(
    session: AsyncSession,
    limit: int,
    name_query: Optional[str] = None,
    cursor_data: Optional[tuple] = None,  # (last_name, last_id)
) -> Sequence[User]:
    """
    Запрос на получение отфильтрованного и отсортированного списка пользователей
    """

    query = select(User)

    # Применяем фильтрацию по имени
    if name_query:
        query = query.where(User.full_name.ilike(f"%{name_query}%"))

    # Применяем фильтрацию курсором
    if cursor_data:
        last_name, last_id = cursor_data
        query = query.where(tuple_(User.full_name, User.id) > (last_name, last_id))

    # Применяем сортировку и лимит
    query = query.order_by(User.full_name).limit(limit)

    result = await session.execute(query)

    return result.scalars().all()


async def get_user_by_email_or_phone(session: AsyncSession, user: str) -> User | None:
    query = select(User).where(
        or_(
            User.phone == user,
            User.email == user,
        )
    )
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def get_user_perms(session: AsyncSession, user_identity: str):
    """Функция для получения данный пользователя включая группы, корзину и разрешения"""

    query = (
        select(User)
        .where(
            or_(
                User.phone == user_identity,
                User.email == user_identity,
            )
        )
        .options(selectinload(User.roles).selectinload(Role.permissions), selectinload(User.cart))
    )
    user = (await session.execute(query)).scalar_one_or_none()

    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id)
    result = (await session.execute(query)).scalar_one_or_none()
    return result


# async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
#     query = select(User).where(User.email == email)
#     result = (await session.execute(query)).scalar_one_or_none()
#     return result
#
#
# async def get_user_by_phone(session: AsyncSession, phone: str) -> User | None:
#     query = select(User).where(User.phone == phone)
#     result = (await session.execute(query)).scalar_one_or_none()
#     return result
