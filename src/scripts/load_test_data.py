import asyncio
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from src.config.database import db_handler
from src.config.settings import get_settings
from src.models.product import Product

settings = get_settings()

db_handler.init_db(
    database_url=str(settings.DATABASE_ASYNC_URL),
    echo=settings.DEBUG,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
)

# --- Разрешения ---
TARGET_PRODUCTS = [
    {
        "id": i,
        "name": f"prod{i}",
        "price": i*100,
        "quantity": i*10,
        "is_active": True
    } for i in range(200, 400)
]


async def default_settings():
    async for session in db_handler.session_getter():
        try:
            print("--- Синхронизация продуктов ---")

            # Создаем инструкцию вставки
            stmt = insert(Product).values(TARGET_PRODUCTS)

            # Добавляем правило: если ID совпадает, обновить остальные поля
            # Это позволит запускать скрипт многократно без ошибок
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['id'], # Название вашего PK поля
                set_={
                    "name": stmt.excluded.name,
                    "price": stmt.excluded.price,
                    "quantity": stmt.excluded.quantity,
                    "is_active": stmt.excluded.is_active,
                }
            )

            await session.execute(upsert_stmt)
            await session.commit()

            print(f"✅ Успешно добавлено {len(TARGET_PRODUCTS)} записей!")
            return

        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при синхронизации: {e}")
            raise e


if __name__ == "__main__":
    asyncio.run(default_settings())
