import uuid
from locust import HttpUser, task, between

# class FastApiStoreUser(HttpUser):
#     # Время между запросами от одного "пользователя"
#     host = "http://51.250.96.208//"
#     wait_time = between(1, 3)
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
    # @task(3)
    # def view_all_users(self):
    #     """Тест чтения: просто заходим на страницу списка"""
    #     self.client.get("/users/")


class FastApiStoreUser(HttpUser):
    host = "http://51.250.96.208//"
    wait_time = between(0.2, 1) # Сократим паузу, чтобы создать реальное давление

    @task
    def view_users(self):
        # Меняй limit прямо в коде или через админку Locust
        limit = 10
        self.client.get(f"/users/?limit={limit}")



# class DjangoSchoolUser(HttpUser):
#     host = "http://103.76.53.242/"
#     # Время ожидания между действиями "ботов"
#     wait_time = between(1, 3)
#
#     @task(1)
#     def register_user(self):
#         """Тест регистрации в Django"""
#         unique_id = str(uuid.uuid4())[:8]
#         password = "StrongPass123!"
#
#         payload = {
#             "email": f"django_test_{unique_id}@example.com",
#             "password1": password,
#             "password2": password,
#             "phone": f"+7999{uuid.uuid4().int % 10000000:07d}",
#             "country": "RU",
#             # avatar пропускаем, так как это FileField, либо передаем null
#             "avatar": None
#         }
#
#         # В Django эндпоинты часто требуют завершающий слэш (trailing slash)
#         with self.client.post("/register/", json=payload, catch_response=True) as response:
#             if response.status_code == 201:
#                 response.success()
#             else:
#                 response.failure(f"Status: {response.status_code}, Body: {response.text}")


# class DjangoSchoolUserLessons(HttpUser):
#     host = "http://103.76.53.242/"  # Теперь этот хост будет по умолчанию
#     wait_time = between(0.1, 0.5) # Сократим паузу, чтобы создать реальное давление
#
#     @task
#     def view_lessons(self):
#         # Меняй limit прямо в коде или через админку Locust
#         limit = 10
#         self.client.get(f"/lesson/?page=1&page_size={limit}")
