import uuid


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


def test_register_creates_user_without_leaking_password(client):
    email = _unique_email("auth_register")
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "Test1234!", "full_name": "Auth Test", "role": "student"},
    )
    assert response.status_code == 201    
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "student"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_is_rejected(client):
    email = _unique_email("auth_dup")
    payload = {"email": email, "password": "Test1234!", "full_name": "Dup", "role": "student"}

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 400


def test_login_success_returns_bearer_token(client):
    email = _unique_email("auth_login")
    client.post(
        "/auth/register",
        json={"email": email, "password": "Test1234!", "full_name": "Login User", "role": "student"},
    )
    response = client.post("/auth/login", data={"username": email, "password": "Test1234!"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    email = _unique_email("auth_wrong")
    client.post(
        "/auth/register",
        json={"email": email, "password": "Test1234!", "full_name": "Wrong Pw", "role": "student"},
    )
    response = client.post("/auth/login", data={"username": email, "password": "WrongPassword!"})
    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = client.post("/auth/login", data={"username": "nobody@example.com", "password": "whatever"})
    assert response.status_code == 401


def test_get_me_without_token_returns_401(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_me_returns_current_authenticated_user(client, make_user):
    user = make_user("student")
    response = client.get("/users/me", headers=user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user["email"]
    assert body["role"] == "student"
