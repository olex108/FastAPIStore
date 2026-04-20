from fastapi import Depends, HTTPException, status
from typing import List, Annotated
from src.models import User, Role, Permission
from src.services.auth import AuthUserService # Ваш сервис получения текущего пользователя

forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="У вас недостаточно прав для выполнения этого действия"
    )


class PermissionChecker:
    """
    Класс для работы с разрешениями прав доступа.

    Инициализирует список разрешений
    При вызове возвращает переданного пользователя или вызывает HTTP_403_FORBIDDEN
    """

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    async def __call__(self, current_user: Annotated[User, Depends(AuthUserService.get_current_active_user)]) -> User:

        if await self.__check_permissions(current_user):
            return current_user
        else:
            raise forbidden_exception

    async def __check_permissions(self, current_user: User) -> bool:

        # Суперюзер всегда имеет доступ
        if current_user.is_superuser:
            return True

        user_permissions = list()
        for role in current_user.roles:
            user_permissions.extend([perm.name for perm in role.permissions])

        if len(set(self.required_permissions).intersection(user_permissions)) > 0:
            return True
        else:
            return False


class OwnerOrPermissionChecker:
    """
    Класс для проверки прав владельца страницы или разрешения прав доступа.

    Проверяет текущего пользователя собственником страницы.
    Инициализирует список разрешений
    При вызове возвращает переданного пользователя или вызывает HTTP_403_FORBIDDEN
    """

    def __init__(self, required_permissions: List[str] = None):
        self.required_permissions = required_permissions

    async def __call__(self, user_id: int, current_user: Annotated[User, Depends(AuthUserService.get_current_active_user)]) -> User:

        # Проверка является ли текущий пользователь владельцем
        if current_user.id == user_id:
            return current_user

        # Проверка есть ли у пользователя нужные разрешения
        elif self.required_permissions:
            if await self.__check_permissions(current_user):
                return current_user
            else:
                raise forbidden_exception
        else:
            raise forbidden_exception


    async def __check_permissions(self, current_user: User) -> bool:

        # Суперюзер всегда имеет доступ
        if current_user.is_superuser:
            return True

        # Получаем список разрешений текущего пользователя
        user_permissions = list()
        for role in current_user.roles:
            user_permissions.extend([perm.name for perm in role.permissions])

        # сравниваем разрешения пользователя с необходимыми
        if len(set(self.required_permissions).intersection(user_permissions)) > 0:
            return True
        else:
            return False



