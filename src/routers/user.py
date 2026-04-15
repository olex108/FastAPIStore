# routers/user.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.crud.user import create_new_user, get_all_users
from src.schemas.user import UserInfo, UserRegister

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserInfo)
async def register_user(user: UserRegister, session: AsyncSession = Depends(db_handler.session_getter)):
    try:
        new_user = await create_new_user(user=user, session=session)
        return new_user
    except Exception as e:
        raise e


@router.get("/", response_model=List[UserInfo])
async def get_users(session: AsyncSession = Depends(db_handler.session_getter)):
    users = await get_all_users(session=session)
    return users
