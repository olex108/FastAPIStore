from src.main import main_app
from fastapi.testclient import TestClient

client = TestClient(main_app)


def test_register_user():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}