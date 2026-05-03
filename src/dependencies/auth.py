# dependencies/auth.py
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import db_handler
from src.config.settings import get_settings
from src.crud.user import get_user_perms
from src.models.user import User

settings = get_settings()
security = HTTPBearer()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class AuthUserDependencies:

    @staticmethod
    async def get_current_user(
        # Теперь получаем объект credentials, в котором лежит токен
        auth: Annotated[HTTPAuthorizationCredentials, Security(security)],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)],
    ) -> User:
        """
        Зависимость для получения пользователя
        """

        token = auth.credentials  # Извлекаем сам токен из объекта
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_identity = payload.get("sub")
            if user_identity is None:
                raise credentials_exception
        except PyJWTError:
            raise credentials_exception

        user = await get_user_perms(session=session, user_identity=user_identity)
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """
        Зависимость для получения авторизированного активного пользователя
        """

        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
