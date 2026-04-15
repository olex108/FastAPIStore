import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from pwdlib import PasswordHash

from src.config.settings import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

debug_logger = logging.getLogger("debug")


class TokenHandler:
    @staticmethod
    def create_access_token(data: dict) -> str:
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

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """Декодирование токена"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except PyJWTError as e:
            debug_logger.debug(f"--- Decode token failed (PyJWTError): {e} ---")
            return None

    @staticmethod
    def get_user_identity_by_token(token: str) -> str | None:
        """Декодирование токена"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_identity = payload.get("sub")
            return user_identity
        except PyJWTError as e:
            debug_logger.debug(f"--- Decode token failed (PyJWTError): {e} ---")
            return None


class PasswordHandler:
    """Сервис для работы с хешированными паролями"""

    password_hash: PasswordHash = PasswordHash.recommended()
    DUMMY_HASH: str = password_hash.hash("dummypassword")

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        return cls.password_hash.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password) -> str:
        return cls.password_hash.hash(password)

    @classmethod
    def dammy_verify(cls, password) -> bool:
        cls.verify_password(password, cls.DUMMY_HASH)
        return False
