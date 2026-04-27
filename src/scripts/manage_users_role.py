# scripts/manage_users_role.py

import asyncio

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from src.config.database import db_handler
from src.config.settings import get_settings
from src.models import Role, RoleUsers, User

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


async def get_user_by_identity(session, identity: str):
    """Поиск пользователя по ID или Email"""
    if identity.isdigit():
        stmt = select(User).where(User.id == int(identity))
    else:
        stmt = select(User).where(User.email == identity)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def interactive_user_roles():
    async for session in db_handler.session_getter():
        while True:
            roles = await get_roles(session)
            print("\n" + "=" * 30)
            print("   УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ")
            print("=" * 30)
            for r in roles:
                print(f"{r.id:2} - {r.name}")
            print(" 0 - Выход")

            choice = input("\nВыберите ID роли для просмотра списка: ")
            if choice == "0":
                return

            try:
                role_id = int(choice)
                # Загружаем роль вместе с пользователями
                stmt = select(Role).where(Role.id == role_id).options(selectinload(Role.users))
                role = (await session.execute(stmt)).scalar_one_or_none()

                if not role:
                    print(f"❌ Роль с ID {role_id} не найдена!")
                    continue

                while True:
                    print(f"\n--- Роль: {role.name.upper()} ---")
                    print("Участники:")
                    user_ids = [u.id for u in role.users]

                    if not role.users:
                        print("  (в этой роли нет пользователей)")
                    else:
                        for u in role.users:
                            print(f"  [{u.id}] {u.full_name} ({u.email})")

                    action = input("\nВыберите действие (+ добавить юзера, - убрать юзера, b назад): ").lower()

                    if action == "b":
                        break

                    elif action == "-":
                        u_id = int(input("Введите ID пользователя для удаления из роли: "))
                        stmt_del = delete(RoleUsers).where(RoleUsers.role_id == role.id, RoleUsers.user_id == u_id)
                        await session.execute(stmt_del)
                        await session.commit()
                        await session.refresh(role)
                        print("✅ Пользователь удален из роли!")

                    elif action == "+":
                        identity = input("Введите ID или Email пользователя: ")
                        user = await get_user_by_identity(session, identity)

                        if not user:
                            print("❌ Пользователь не найден!")
                            continue

                        if user.id in user_ids:
                            print(f"⚠️ {user.full_name} уже имеет эту роль!")
                        else:
                            new_link = RoleUsers(role_id=role.id, user_id=user.id)
                            session.add(new_link)
                            await session.commit()
                            await session.refresh(role)
                            print(f"✅ {user.full_name} добавлен в роль {role.name}!")
                    else:
                        break

            except ValueError:
                print("❌ Введите число!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await session.rollback()


if __name__ == "__main__":
    print("🚀 Запуск менеджера пользователей в ролях...")
    try:
        asyncio.run(interactive_user_roles())
    except KeyboardInterrupt:
        print("\n👋 Завершено.")
