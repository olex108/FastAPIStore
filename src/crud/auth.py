from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import RefreshSession
from src.models.user import User


async def create_refresh_session(user: User, refresh_token: str, session: AsyncSession) -> RefreshSession:
    new_session = RefreshSession(
        user_id=user.id,
        refresh_token=refresh_token,
    )
    session.add(new_session)
    await session.commit()
    await session.refresh(new_session)
    return new_session


async def get_refresh_session_by_token(refresh_token: str, session: AsyncSession) -> RefreshSession | None:
    query = select(RefreshSession).where(RefreshSession.refresh_token == refresh_token)
    result = (await session.execute(query)).scalar_one_or_none()
    return result
