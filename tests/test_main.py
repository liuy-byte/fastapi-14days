from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_returns_hello_world():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_about_returns_project_info():
    response = client.get("/about")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "fastapi-14days"


def test_greet_with_name():
    response = client.get("/greet/Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice!"}


def test_greet_with_different_name():
    response = client.get("/greet/Bob")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Bob!"}
