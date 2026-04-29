import uuid
from locust import HttpUser, task, between

# class FastApiStoreUser(HttpUser):
#     # Время между запросами от одного "пользователя"
#     wait_time = between(1, 2)
#
#     @task(1)
#     def register_new_user(self):
#         """Тест регистрации: создаем уникальные данные для каждого запроса"""
#
#         unique_id = str(uuid.uuid4())[:8]
#         payload = {
#             "email": f"test_{unique_id}@example.com",
#             "password": "Password!",
#             "confirm_password": "Password!",
#             "full_name": f"Locus User {unique_id}",
#             "phone": f"+7999{uuid.uuid4().int % 10000000:07d}"
#         }
#         # Отправляем запрос на регистрацию
#         with self.client.post("/users/register", json=payload, catch_response=True) as response:
#             if response.status_code == 201:
#                 response.success()
#             else:
#                 response.failure(f"Registration failed: {response.text}")
#
#     @task(3)
#     def view_all_users(self):
#         """Тест чтения: просто заходим на страницу списка"""
#         self.client.get("/users/")


class FastApiStoreUser(HttpUser):
    wait_time = between(0.1, 0.5) # Сократим паузу, чтобы создать реальное давление

    @task
    def view_users(self):
        # Меняй limit прямо в коде или через админку Locust
        limit = 50
        self.client.get(f"/users/?limit={limit}")