from src.models.user import User
from src.crud.user import get_user_by_email_or_phone
from src.services.password import PasswordHandler
from src.crud.auth import create_refresh_session

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_settings

from datetime import datetime, timedelta, timezone
from typing import Annotated, Tuple

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthUserService:
    @staticmethod
    async def authenticate_user(session: AsyncSession, user_identity: str, password: str) -> Tuple[User, str] | None:
        """
        Метод для аутентификации пользователя
        """

        user = await get_user_by_email_or_phone(session=session, user_identity=user_identity)
        if not user:
            return PasswordHandler.dammy_verify(password)
        else:
            if not PasswordHandler.verify_password(password, user.hashed_password):
                return None
        return user, user_identity

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        """Создание access токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Создание refresh токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt


    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
        pass
        # credentials_exception = HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Could not validate credentials",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        # try:
        #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        #     username = payload.get("sub")
        #     if username is None:
        #         raise credentials_exception
        #     token_data = TokenData(username=username)
        # except InvalidTokenError:
        #     raise credentials_exception
        # user = get_user(fake_users_db, username=token_data.username)
        # if user is None:
        #     raise credentials_exception
        # return user

    async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
