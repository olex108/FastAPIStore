import logging
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, Role
from src.schemas.user import UserRegister
from src.services.security import PasswordHandler

debug_logger = logging.getLogger("debug")


async def create_new_user(user: UserRegister, session: AsyncSession):
    data = user.model_dump(exclude={"confirm_password"})
    data["hashed_password"] = PasswordHandler.get_password_hash(data.pop("password"))

    # Убрать поле при добавлении системы верификации пользователя !!!!!!!!!!!!
    data["is_active"] = True

    new_user = User(**data)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        debug_logger.info(f"Created new user {new_user}")
    except IntegrityError as e:
        await session.rollback()
        debug_logger.debug(f"--- Create user failed (IntegrityError): {e} ---")
        raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create user failed: {e} ---")
        raise e

    return new_user


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    query = select(User).order_by(User.id)
    result = await session.scalars(query)
    return result.all()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def get_user_by_phone(session: AsyncSession, phone: str) -> User | None:
    query = select(User).where(User.phone == phone)
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def get_user_by_email_or_phone(session: AsyncSession, user_identity: str) -> User | None:
    query = select(User).where(
        or_(
            User.phone == user_identity,
            User.email == user_identity,
        )
    )
    result = (await session.execute(query)).scalar_one_or_none()
    return result


async def get_user_perms(session: AsyncSession, user_identity: str):
    """Функция для получения данный пользователя включая группы и разрешения"""

    query = (
        select(User)
        .where(
            or_(
                User.phone == user_identity,
                User.email == user_identity,
            )
        )
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
    )

    user = (await session.execute(query)).scalar_one_or_none()
    # if user:
    #     print(f"--- Пользователь: {user.full_name} (ID: {user.id}) ---")
    #
    #     # Проверяем группы
    #     print(f"Группы ({len(user.roles)}):")
    #     for role in user.roles:
    #         # Для каждой группы проверяем разрешения
    #         perm_names = [p.name for p in role.permissions]
    #         print(f" - Группа: {role.name} | Разрешения: {', '.join(perm_names)}")
    # else:
    #     print("Пользователь не найден")
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id)
    result = (await session.execute(query)).scalar_one_or_none()
    return result
