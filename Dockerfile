# Dockerfile
# Указываем базовый образ
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install "poetry==$POETRY_VERSION"


# Копируем файл с зависимостями и устанавливаем их
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости с помощью Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем остальные файлы проекта в контейнер
COPY . .

RUN mkdir -p /app/media/orders /app/logs

# Открываем порт для взаимодействия с приложением
EXPOSE 8080

# Определяем команду для запуска приложения
CMD ["python", "src/main.py"]
