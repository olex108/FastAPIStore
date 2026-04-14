from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User


async def get_user_by_email(session: AsyncSession, email):
    pass


async def get_user_by_phone(session: AsyncSession, phone):
    pass


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    query = select(User).order_by(User.id)
    result = await session.scalars(query)
    return result.all()
