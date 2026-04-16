from fastapi import Depends, HTTPException, status
from typing import List
from src.models import User, Role, Permission
from src.services.auth import AuthUserService # Ваш сервис получения текущего пользователя


class PermissionChecker:
    """
    Класс для работы с разрешениями прав доступа.

    Инициализирует список разрешений
    При вызове возвращает переданного пользователя или вызывает HTTP_403_FORBIDDEN
    """

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
        print("PERMISSIONS ----------> ", required_permissions)

    async def __call__(self, current_user: User = Depends(AuthUserService.get_current_user)) -> User | None:
        # Суперюзер всегда имеет доступ
        if current_user.is_superuser:
            return current_user

        # Собираем все разрешения пользователя из всех его ролей
        user_permissions = list()
        for role in current_user.roles:
            user_permissions.extend([perm for perm in role.permissions])

        print("PERMISSIONS ----------> ", self.required_permissions)

        print("Permissions  -----> ",user_permissions)

        # Проверяем наличие нужных разрешений
        # Если хотя бы одно из требуемых разрешений есть у пользователя — пускаем
        if len(set(self.required_permissions).intersection(user_permissions)) > 0:
            return current_user
        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия"
            )
