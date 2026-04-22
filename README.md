# FastAPIStore

# 1. Сборка образа (выполняй при изменении кода или зависимостей)
docker-compose build

# 2. Запуск баз данных (основной и тестовой) в фоновом режиме
docker-compose up -d db test_db

# 3. Проверка, что базы поднялись (статус должен быть healthy)
docker-compose ps

# Остановить и удалить старые контейнеры
docker-compose down


