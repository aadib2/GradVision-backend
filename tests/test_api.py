from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_backend_starts():
    response = client.get("/docs")
    assert response.status_code == 200


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_list_universities():
    response = client.get("/api/universities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_papers():
    response = client.get("/api/papers")
    assert response.status_code == 200


def test_program_not_found():
    response = client.get("/api/program/999999")
    assert response.status_code == 404