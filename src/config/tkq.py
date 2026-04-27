# config/tkq.py
import taskiq_fastapi
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.config.settings import get_settings


redis_url = get_settings().REDIS_SETTINGS.REDIS_URL

# Настраиваем хранилище результатов и брокер
result_backend = RedisAsyncResultBackend(redis_url=redis_url)

broker = ListQueueBroker(url=redis_url).with_result_backend(result_backend)

# Интеграция с FastAPI для использования Dependency Injection внутри задач
taskiq_fastapi.init(broker, "src.main:main_app")
