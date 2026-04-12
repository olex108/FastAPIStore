import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .config.database import db_handler
from .config.logger import LOGGING_CONFIG
from .config.settings import get_settings
from .routers import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Благодаря декоратору @asynccontextmanager создаем асинхронный контекстный менеджер

    Часть до yield выполняется в методе aenter
    Часть после выполнится в aexit
    :param app:
    :return:
    """

    # startup
    debug_logger = logging.getLogger("debug")
    debug_logger.debug("--- Lifespan start ---")
    yield
    # shutdown
    debug_logger.debug("--- Lifespan shutdown ---")
    await db_handler.dispose()


main_app = FastAPI(lifespan=lifespan)

main_app.include_router(user.router)


if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run("src.main:main_app", host=settings.HOST, port=settings.PORT, reload=True, log_config=LOGGING_CONFIG)
