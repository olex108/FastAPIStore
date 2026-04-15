from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

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
