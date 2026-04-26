import pytest
from fastapi import HTTPException
from src.dependencies.permissions import PermissionChecker
from src.models.user import User, Role, Permission


@pytest.mark.asyncio
async def test_permission_checker_superuser():
    # Суперпользователь всегда проходит
    checker = PermissionChecker(required_permissions=["delete_user"])
    user = User(is_superuser=True, is_active=True, roles=[])

    result = await checker(current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_permission_checker_success():
    # Обычный пользователь с нужной ролью и пермишеном
    perm = Permission(name="edit_post")
    role = Role(name="editor", permissions=[perm])
    user = User(is_superuser=False, is_active=True, roles=[role])

    checker = PermissionChecker(required_permissions=["edit_post"])
    result = await checker(current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_permission_checker_forbidden():
    # Пользователь без нужных прав вызывает 403
    role = Role(name="guest", permissions=[])
    user = User(is_superuser=False, is_active=True, roles=[role])

    checker = PermissionChecker(required_permissions=["admin_access"])
    with pytest.raises(HTTPException) as exc:
        await checker(current_user=user)
    assert exc.value.status_code == 403


from src.dependencies.permissions import OwnerOrPermissionChecker


@pytest.mark.asyncio
async def test_owner_checker_is_owner():
    # Текущий пользователь и есть владелец (user_id совпадает)
    checker = OwnerOrPermissionChecker()
    user = User(id=10, is_active=True, roles=[])

    # Передаем id=10, что совпадает с user.id
    result = await checker(user_id=10, current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_owner_checker_not_owner_but_has_perm():
    # Не владелец, но имеет "модераторское" разрешение
    perm = Permission(name="manage_all")
    role = Role(name="mod", permissions=[perm])
    user = User(id=1, is_active=True, roles=[role])

    checker = OwnerOrPermissionChecker(required_permissions=["manage_all"])
    # user_id=99 (не владелец), но тест должен пройти
    result = await checker(user_id=99, current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_owner_checker_fail():
    # И не владелец, и нет прав
    user = User(id=1, is_active=True, roles=[])
    checker = OwnerOrPermissionChecker(required_permissions=["admin"])

    with pytest.raises(HTTPException) as exc:
        await checker(user_id=99, current_user=user)
    assert exc.value.status_code == 403
