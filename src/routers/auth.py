# routers/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.security import PasswordHandler, TokenHandler
from src.config.database import db_handler
from src.config.settings import get_settings

from src.crud.auth import create_refresh_session, get_refresh_session_by_token
from src.crud.user import get_user_by_id, get_user_by_email_or_phone
from src.schemas.auth import Token
from src.schemas.user import UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

settings = get_settings()

exception_false_auth = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email, phone or password",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/login")
async def login(
    user: UserLogin,
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
) -> Token:
    """
    Эндпоинт для аутентификации пользователя.
    Получает JSON с полями user и password,
    В поле user может храниться почта или телефон пользователя

    В случае если таких данных нет в базе данных возвращает ошибку 401
    """

    try:
        # Получаем пользователя из базы данных
        user_obj= await get_user_by_email_or_phone(session=session, user=user.user)

        if not user_obj:
            PasswordHandler.dammy_verify(user.password)
            raise exception_false_auth
        else:
            if not PasswordHandler.verify_password(user.password, user_obj.hashed_password):
                raise exception_false_auth

        access_token = TokenHandler.create_access_token(data={"sub": user.user})
        refresh_token = TokenHandler.create_refresh_token(data={"sub": user.user})
        # Записываем refresh_token в базу данных
        await create_refresh_session(user=user_obj, session=session, refresh_token=refresh_token)

        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    except Exception as error:
        raise exception_false_auth


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: Annotated[str, Header()],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
):
    """
    Эндпоинт для обновления access токена с помощью refresh токена.
    Получает refresh токен, делает запрос в базу данных на получения user_id.
    Проверяет наличие данного пользователя в базе данных.

    В случае если refresh токена или пользователя нет в базе данных возвращает ошибку 401
    """

    refresh_session = await get_refresh_session_by_token(refresh_token=refresh_token, session=session)
    if refresh_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await get_user_by_id(session=session, user_id=refresh_session.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_identity = TokenHandler.get_user_identity_by_token(refresh_token)
    new_access_token = TokenHandler.create_access_token(data={"sub": user_identity})

    return {"access_token": new_access_token, "refresh_token": refresh_token, "token_type": "bearer"}
