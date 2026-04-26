import asyncio
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from src.config.database import db_handler
from src.config.settings import get_settings
from src.models import Role, Permission, RolePermissions

settings = get_settings()

db_handler.init_db(
    database_url=str(settings.DATABASE_ASYNC_URL),
    echo=settings.DEBUG,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
)

# --- Разрешения ---
TARGET_PERMISSIONS = [
    "products:view",
    "products:create",
    "products:update",
    "products:delete",

    "users:view",
    "users:update",
    "users:delete",

    "carts:view",
    "carts:update",
    "carts:delete",
]

# --- Роли ---
TARGET_ROLES = [
    "Admin",
    "Manager",
    "Customer",
]

TARGET_PERMISSIONS_ROLES = {
    "Admin": [
        "products:view",
        "products:create",
        "products:update",
        "products:delete",

        "users:view",
        "users:update",
        "users:delete",

        "carts:view",
        "carts:update",
        "carts:delete",
    ],
    "Manager": [
        "products:view",

        "users:view",

        "carts:view",
        "carts:update",
        "carts:delete",
    ],
    "Customer": [
        "products:view",
    ]
}

async def default_settings():
    # Получаем сессию один раз для всех действий
    async for session in db_handler.session_getter():
        try:
            # --- 1. Синхронизация разрешений ---
            print("--- Синхронизация разрешений ---")
            await session.execute(delete(Permission).where(Permission.name.not_in(TARGET_PERMISSIONS)))

            res_p = await session.execute(select(Permission.name))
            existing_p = res_p.scalars().all()
            for p_name in TARGET_PERMISSIONS:
                if p_name not in existing_p:
                    session.add(Permission(name=p_name))
                    print(f"Добавлено разрешение: {p_name}")

            # --- 2. Синхронизация ролей ---
            print("--- Синхронизация ролей ---")
            await session.execute(delete(Role).where(Role.name.not_in(TARGET_ROLES)))

            res_r = await session.execute(select(Role.name))
            existing_r = res_r.scalars().all()
            for r_name in TARGET_ROLES:
                if r_name not in existing_r:
                    session.add(Role(name=r_name))
                    print(f"Добавлена роль: {r_name}")

            # --- 3. Синхронизация разрешений для ролей ---
            print("--- Синхронизация разрешений для ролей ---")

            # Сначала фиксируем добавленные роли и права в БД, чтобы получить их ID
            await session.flush()

            # Удаляем старые связи
            await session.execute(delete(RolePermissions))

            # Получаем маппинг имен к ID
            res_roles = await session.execute(select(Role))
            roles_map = {r.name: r.id for r in res_roles.scalars().all()}

            res_perms = await session.execute(select(Permission))
            perms_map = {p.name: p.id for p in res_perms.scalars().all()}

            # Заполняем таблицу связей
            for role_name, perms_list in TARGET_PERMISSIONS_ROLES.items():
                role_id = roles_map.get(role_name)

                if not role_id:
                    continue

                for p_name in perms_list:
                    perm_id = perms_map.get(p_name)
                    if perm_id:
                        session.add(RolePermissions(role_id=role_id, permission_id=perm_id))

            print("Связи ролей и разрешений обновлены")


            # Фиксируем всё одним коммитом
            await session.commit()
            print("✅ Все данные успешно синхронизированы!")
            return  # Выходим из генератора

        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при синхронизации: {e}")
            raise e


if __name__ == "__main__":
    asyncio.run(default_settings())