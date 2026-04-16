# routers/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.config.settings import get_settings
from src.crud.auth import create_refresh_session, get_refresh_session_by_token
from src.crud.user import get_user_by_id
from src.schemas.auth import Token
from src.services.auth import AuthUserService
from src.services.security import TokenHandler

router = APIRouter(
    prefix="/auth", tags=["Auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
) -> Token:
    """
    Эндпоинт для аутентификации пользователя.
    Получает форму с полями username и password,
    В поле username может храниться почта или телефон пользователя

    В случае если таких данных нет в базе данных возвращает ошибку 401

    :param form_data: форма для получения данных от пользователя
    :param session: AsyncSession
    :return: Token
    """

    # Получаем пользователя из базы данных
    user, user_identity = await AuthUserService.authenticate_user(
        session=session, user_identity=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = TokenHandler.create_access_token(data={"sub": user_identity})
    refresh_token = TokenHandler.create_refresh_token(data={"sub": user_identity})
    # Записываем refresh_token в базу данных
    await create_refresh_session(user=user, session=session, refresh_token=refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


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

    :param refresh_token:
    :param session: AsyncSession
    :return: Token
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
