from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.config.settings import get_settings
from src.schemas.auth import Token
from src.services.auth import AuthUserService
from src.crud.auth import create_refresh_session

from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_handler.session_getter),
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
    user, user_identity = await AuthUserService.authenticate_user(session=session, user_identity=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthUserService.create_access_token(data={"sub": user_identity}, expires_delta=access_token_expires)
    refresh_token = AuthUserService.create_refresh_token(data={"sub": user_identity})
    await create_refresh_session(user=user, session=session, refresh_token=refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
