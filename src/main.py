# main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.database import db_handler
from src.config.tkq import broker

from .config.logger import LOGGING_CONFIG
from .config.settings import get_settings
from .middlewares.access_logging import LogMiddleware
from .routers import auth, cart, product, user, order

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Благодаря декоратору @asynccontextmanager создаем асинхронный контекстный менеджер
    """

    # startup
    # Инициализация Taskiq
    if not broker.is_worker_process:
        await broker.startup()
    # Инициализируем зависимости сессий подключения к БД
    db_handler.init_db(
        database_url=str(settings.DATABASE_ASYNC_URL),
        echo=settings.DEBUG,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
    )
    debug_logger = logging.getLogger("debug")
    debug_logger.debug("--- Lifespan start ---")
    yield
    # shutdown
    debug_logger.debug("--- Lifespan shutdown ---")
    # Отключение Taskiq
    if not broker.is_worker_process:
        await broker.shutdown()
    # Отключение БД
    await db_handler.dispose()


main_app = FastAPI(lifespan=lifespan)

# Добавляем middleware
main_app.add_middleware(LogMiddleware)
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# if settings.DEBUG and settings.DEBUG_TOOLBAR:
#     main_app.add_middleware(
#         DebugToolbarMiddleware,
#         panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
#         session_generators=["src.config.database:db_handler.session_getter"],
#     )

main_app.include_router(user.router)
main_app.include_router(product.router)
main_app.include_router(auth.router)
main_app.include_router(cart.router)
main_app.include_router(order.router)


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run("src.main:main_app", host=settings.HOST, port=settings.PORT, reload=True, log_config=LOGGING_CONFIG)
