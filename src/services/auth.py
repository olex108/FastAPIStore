from typing import Annotated, Tuple

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings
from src.config.database import db_handler
from src.crud.user import get_user_by_email_or_phone, get_user_perms
from src.models.user import User
from src.schemas.user import UserInfo
from src.services.security import PasswordHandler

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthUserService:
    @staticmethod
    async def authenticate_user(session: AsyncSession, user_identity: str, password: str) -> Tuple[User, str] | None:
        """
        Метод для аутентификации пользователя
        """

        user = await get_user_by_email_or_phone(session=session, user_identity=user_identity)
        if not user:
            PasswordHandler.dammy_verify(password)
            return None
        else:
            if not PasswordHandler.verify_password(password, user.hashed_password):
                return None
        return user, user_identity

    @staticmethod
    async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[AsyncSession, Depends(db_handler.session_getter)]
    ) -> User:
        """
        Метод для получения авторизированного пользователя
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
