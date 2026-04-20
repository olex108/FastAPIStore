# schemas/user.py
import logging
import re
from typing import Self

from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    model_validator,
    ConfigDict
)

debug_logger = logging.getLogger("debug")


class UserInfo(BaseModel):
    """Схема для передачи ответа информации о пользователе"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""

    full_name: str
    email: EmailStr
    phone: str
    password: str
    confirm_password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """
        Метод для валидации номера телефона с условиями:
        Телефон должен начинаться с +7 и содержать 10 цифр
        """

        if phone[:2] != "+7":
            raise ValueError("Номер телефона должен начинаться с +7")
        if len(phone) != 12:
            raise ValueError("Номер телефона должен содержать 10 цифр после +7")
        if not phone[-2:].isdigit():
            raise ValueError("Номер телефона должен составлять только цифры")
        return phone

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Метод для валидации пароля с условиями:
         - Пароль должен соответствовать следующим требованиям: не менее 8 символов,
         - только латиница,
         - минимум 1 символ верхнего регистра,
         - минимум 1 спец символ ($%&!:)
        """

        if len(password) < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов")

        # 2. Проверка: только латиница, цифры и спецсимволы (запрет кириллицы)
        if not re.match(r"^[a-zA-Z0-9$%&!:]+$", password):
            raise ValueError("Пароль может содержать только латиницу и спецсимволы ($%&!:)")

        # 3. Минимум 1 символ верхнего регистра
        if not any(char.isupper() for char in password):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        # 4. Минимум 1 спецсимвол ($%&!:)
        if not any(char in "$%&!:" for char in password):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол ($%&!:)")

        return password

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        """Проверка на совпадения полей пароля"""

        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class UserLogin(BaseModel):
    """Схема для аутентификации пользователя"""

    user: str
    password: str


class UserUpdate(BaseModel):
    """Схема для изменения полей пользователя"""

    id: int
    full_name: str
    email: EmailStr
    phone: str
    is_active: bool
    is_superuser: bool
