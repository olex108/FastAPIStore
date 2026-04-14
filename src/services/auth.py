from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.config.settings import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



class PasswordHandler:
    """Сервис для работы с хешированными паролями"""

    password_hash: PasswordHash = PasswordHash.recommended()
    DUMMY_HASH: str = password_hash.hash("dummypassword")

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.password_hash.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        return cls.password_hash.hash(password)

    @classmethod
    def dammy_verify(cls, password):
        cls.verify_password(password, cls.DUMMY_HASH)
        return False


class AuthUserService:

    def authenticate_user(self, session: AsyncSession, username: str, password: str):
        """
        Метод для аунтефикации пользователя для получения пользователя или

        :param session:
        :param username:
        :param password:
        :return:
        """
            # def authenticate_user(self, session: AsyncSession, email: str | None, phone: str | None, password: str):
                # if email:
                #     user = get_user_by_email
                # elif phone:
                #     user = get_user_by_phone()

        user = self.get_user(session, username)
        if not user:
            return PasswordHandler.dammy_verify(password)
        if not PasswordHandler.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def get_user(session: AsyncSession, username: str):
        user = session.query(User).filter(User.email == username).first()
        if user:
            # Вариант с преобразованием в пайдентик
            # user_dict = db[username]
            # return UserInDB(**user_dict)

            # Возвращаем модель пользователя
            return user
        else:
            return None

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
