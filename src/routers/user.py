# routers/user.py
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.crud.user import create_new_user, get_all_users
from src.crud.cart import create_cart
from src.models.user import User
from src.schemas.user import UserInfo, UserRegister, UserAuth
from src.services.auth import AuthUserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserInfo)
async def register_user(
    user: UserRegister,
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    try:
        new_user = await create_new_user(user=user, session=session)
        user_cart = await create_cart(new_user, session=session)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"{e}",
        )


@router.get("/", response_model=List[UserInfo])
async def get_users(session: AsyncSession = Depends(db_handler.session_getter)):

    users = await get_all_users(session=session)
    return users


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: Annotated[UserAuth, Depends(AuthUserService.get_current_user)]):

    return current_user
