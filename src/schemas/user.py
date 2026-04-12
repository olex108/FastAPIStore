# schemas/user.py
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str


class UserAuth(BaseModel):
    email: EmailStr
    phone: str
    password: str
