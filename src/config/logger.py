# logger.py
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
    },
    "loggers": {
        "access": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "debug": {
            "handlers": ["stdout"],
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
