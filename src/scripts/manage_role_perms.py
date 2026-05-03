# scripts/manage_role_perms.py
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from src.config.database import db_handler
from src.config.settings import get_settings
from src.models import Permission, Role, RolePermissions

settings = get_settings()

db_handler.init_db(
    database_url=str(settings.DATABASE_ASYNC_URL),
    echo=settings.DEBUG,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
)


async def get_roles(session):
    result = await session.execute(select(Role).order_by(Role.id))
    return result.scalars().all()


async def get_all_permissions(session):
    result = await session.execute(select(Permission).order_by(Permission.id))
    return result.scalars().all()


async def interactive_shell():
    async for session in db_handler.session_getter():
        while True:
            roles = await get_roles(session)
            print("\n" + "=" * 25)
            print("   СПИСОК РОЛЕЙ")
            print("=" * 25)
            for r in roles:
                print(f"{r.id:2} - {r.name}")
            print(" 0 - Выход")

            choice = input("\nВыберите ID роли: ")
            if choice == "0":
                return

            try:
                role_id = int(choice)
                stmt = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
                role = (await session.execute(stmt)).scalar_one_or_none()

                if not role:
                    print(f"❌ Роль с ID {role_id} не найдена!")
                    continue

                while True:
                    print(f"\n--- Роль: {role.name.upper()} ---")
                    print("Текущие разрешения:")
                    current_ids = [p.id for p in role.permissions]

                    if not role.permissions:
                        print("  (пусто)")
                    else:
                        for p in role.permissions:
                            print(f"  [{p.id}] {p.name}")

                    action = input("\nВыберите действие (+ добавить, - удалить, b назад): ").lower()

                    if action == "b":
                        break

                    elif action == "-":
                        p_id = int(input("Введите ID разрешения для удаления: "))
                        # Используем RolePermissions вместо GroupPermissions
                        stmt_del = delete(RolePermissions).where(
                            RolePermissions.role_id == role.id, RolePermissions.permission_id == p_id
                        )
                        await session.execute(stmt_del)
                        await session.commit()
                        await session.refresh(role)
                        print("✅ Удалено")

                    elif action == "+":
                        all_perms = await get_all_permissions(session)
                        print("\nДоступные разрешения:")
                        for ap in all_perms:
                            status = "✅" if ap.id in current_ids else "  "
                            print(f"  {status} {ap.id:2} - {ap.name}")

                        p_id = int(input("\nВведите ID для добавления: "))
                        if p_id in current_ids:
                            print("⚠️ Уже есть")
                        else:
                            # Используем RolePermissions
                            new_link = RolePermissions(role_id=role.id, permission_id=p_id)
                            session.add(new_link)
                            await session.commit()
                            await session.refresh(role)
                            print("✅ Добавлено")
                    else:
                        break

            except ValueError:
                print("❌ Введите корректное число!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await session.rollback()


if __name__ == "__main__":
    asyncio.run(interactive_shell())
