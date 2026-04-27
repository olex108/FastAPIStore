from datetime import datetime, timedelta, timezone
from src.config.settings import get_settings
import jwt


def create_test_auth_token(user_email: str):
    """Генерирует реальный JWT токен для тестов"""
    payload = {"sub": user_email, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
    return jwt.encode(payload, get_settings().SECRET_KEY, algorithm=get_settings().ALGORITHM)
