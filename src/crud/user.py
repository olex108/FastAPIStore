import logging
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException

from src.models.user import User
from src.schemas.user import UserRegister

from src.services.auth import PasswordHandler


debug_logger = logging.getLogger("debug")


async def create_new_user(user: UserRegister, session: AsyncSession):
    data = user.model_dump(exclude={"confirm_password"})
    print(data)
    data["hashed_password"] = PasswordHandler.get_password_hash(data.pop("password"))
    print(data)

    new_user = User(**data)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
    except IntegrityError  as e:
        await session.rollback()
        debug_logger.debug(f"--- Create user failed (IntegrityError): {e} ---")
        raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        await session.rollback()
        debug_logger.error(f"--- Create user failed: {e} ---")
        raise e

    print(f"!!! New user created {new_user} !!!")
    return new_user


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    query = select(User).order_by(User.id)
    result = await session.scalars(query)
    return result.all()


async def get_user_by_email(session: AsyncSession, email):
    pass


async def get_user_by_phone(session: AsyncSession, phone):
    pass


