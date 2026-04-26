import jwt
from datetime import datetime, timedelta, timezone


def create_test_auth_token(user_email: str):
    """Генерирует реальный JWT токен для тестов"""
    payload = {"sub": user_email, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
