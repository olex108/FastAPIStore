import logging
import sys


def setup_logging():
    # Общий формат для всех логов
    formatter = logging.Formatter(
        "%(asctime)s | %(name)-10s | %(levelname)-7s | %(message)s"
    )

    # Настраиваем вывод в консоль (STDOUT)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # 1. Логгер для Middleware (страницы и запросы)
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(stdout_handler)
    access_logger.propagate = False  # Чтобы логи не дублировались в корневом логгере

    # 2. Логгер для дебага (ваши заметки в коде)
    debug_logger = logging.getLogger("debug")
    debug_logger.setLevel(logging.DEBUG)
    debug_logger.addHandler(stdout_handler)
    debug_logger.propagate = False

    # (Опционально) Отключаем стандартный спам uvicorn, если хотите
    # logging.getLogger("uvicorn.access").handlers = []
