# config/tkq.py
import taskiq_fastapi
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.config.settings import get_settings

settings = get_settings()

# Настраиваем хранилище результатов и брокер
result_backend = RedisAsyncResultBackend(redis_url=settings.REDIS_URL)

broker = ListQueueBroker(url=settings.REDIS_URL).with_result_backend(result_backend)

# Интеграция с FastAPI для использования Dependency Injection внутри задач
taskiq_fastapi.init(broker, "src.main:main_app")
