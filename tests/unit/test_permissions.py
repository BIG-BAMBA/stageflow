from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login_flow():
    payload = {"email": "student@example.com", "password": "secret123", "full_name": "Student One", "role": "student"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    login = client.post("/auth/login", data={"username": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_me_requires_authentication():
    response = client.get("/users/me")
    assert response.status_code == 401
