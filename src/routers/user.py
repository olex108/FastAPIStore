from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session
from typing import List


from src.config.database import db_handler
from src.crud.user import get_all_users
from src.schemas.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[User])
async def get_users(session: AsyncSession = Depends(db_handler.session_getter)):
    users = await get_all_users(session=session)
    return users
