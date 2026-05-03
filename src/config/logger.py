import os
from src.config.settings import get_settings

settings = get_settings()

# Создаем папку для логов, если её нет
if not os.path.exists("logs"):
    os.makedirs("logs")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(name)-10s | %(process)d | %(levelname)-7s | %(message)s",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/access.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "access": {
            "handlers": ["stdout", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "debug": {
            # Если DEBUG=True, используем stdout, иначе пустой список (логгер молчит)
            "handlers": ["stdout"] if settings.DEBUG else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
