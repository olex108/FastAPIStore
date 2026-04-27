# import pytest

# from src.crud.user import get_all_users

#
# async def register_user(ac):
#     user_data = {
#         "email": "test2@example.com",
#         "phone": "+79991234568",
#         "password": "Password!",
#         "full_name": "Test User",
#         "confirm_password": "Password!"
#     }
#     await ac.post("/users/register", json=user_data)
#
#
# @pytest.mark.asyncio
# async def test_get_all_users_real_db(override_get_async_session):
#
#     # await register_user(db_session)
#     # 2. Действие: вызываем ТВОЮ функцию
#     users = await get_all_users(override_get_async_session)
#
#     # 3. Проверка
#     assert len(users) == 1
#     # assert users[0].full_name == "Ivan"
#     # assert users[1].full_name == "Maria"
