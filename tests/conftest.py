from httpx import AsyncClient, ASGITransport

from src.config.database import db_handler
from src.models.base import Base


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from src.main import main_app
from sqlalchemy.pool import NullPool

import pytest

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:ae35ad@localhost:5432/test_db"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    # NullPool предотвращает утечки соединений между тестами
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        print("Pre commit")
        conn.run_sync(Base.metadata.drop_all)
        print("Pre commit")
    #     await conn.run_sync(Base.metadata.drop_all)
    # await engine.dispose()


@pytest.fixture
async def ac(engine):
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    # Создаем одну сессию на весь тест
    async with session_factory() as session:
        # ПРЯМАЯ ПОДМЕНА: перехватываем зависимость
        main_app.dependency_overrides[db_handler.session_getter] = lambda: session

        # Используем транспорт БЕЗ lifespan (критично для тестов)
        async with AsyncClient(
                transport=ASGITransport(app=main_app),
                base_url="http://test"
        ) as client:
            yield client

        main_app.dependency_overrides.clear()



# # @pytest.fixture(scope="session")
# # def event_loop():
# #     loop = asyncio.get_event_loop_policy().new_event_loop()
# #     yield loop
# #     loop.close()
#
# @pytest.fixture(scope="session")
# async def engine():
#     engine = create_async_engine(
#         TEST_DATABASE_URL,
#         poolclass=StaticPool,
#         echo=False
#     )
#     from src.config.database import db_handler
#     db_handler.engine = engine
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield engine
#     await engine.dispose()
#
# # @pytest.fixture
# # async def session(engine):
# #     """Фикстура создает изолированную сессию для каждого теста"""
# #     Session = async_sessionmaker(bind=engine, expire_on_commit=False)
# #     print("!!!! Session: ",Session)
# #     async with Session() as session:
# #         yield session
#
#
# @pytest.fixture
# async def ac(engine):

#     main_app.user_middleware = []
#     main_app.middleware_stack = main_app.build_middleware_stack()
#     main_app.router.lifespan_context = None
#
#     session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
#
#     async with session_maker() as session:
#         async def _override_get_db():
#             yield session
#
#     # Заменяем оригинальную зависимость на нашу локальную
#
#     from src.config.database import db_handler
#     main_app.dependency_overrides[db_handler.session_getter] = _override_get_db
#
#     async with AsyncClient(
#             transport=ASGITransport(app=main_app),
#             base_url="http://test"
#     ) as client:
#         yield client
#
#     # main_app.dependency_overrides.clear()

