def test_list_users_forbidden_for_non_admin(client, make_user):
    student = make_user("student")
    response = client.get("/users", headers=student["headers"])
    assert response.status_code == 403


def test_list_users_forbidden_without_authentication(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_admin_can_list_users(client, make_user):
    make_user("student")
    admin = make_user("admin")
    response = client.get("/users", headers=admin["headers"])
    assert response.status_code == 200
    assert any(u["id"] == admin["id"] for u in response.json())


def test_non_admin_cannot_change_role(client, make_user):
    student = make_user("student")
    other = make_user("student")
    response = client.patch(
        f"/users/{other['id']}/role", json={"role": "company"}, headers=student["headers"]
    )
    assert response.status_code == 403


def test_admin_can_force_role_change(client, make_user):
    admin = make_user("admin")
    student = make_user("student")

    response = client.patch(
        f"/users/{student['id']}/role", json={"role": "company"}, headers=admin["headers"]
    )
    assert response.status_code == 200
    assert response.json()["role"] == "company"

    # Le nouveau rôle doit être immédiatement effectif pour les permissions.
    login = client.post("/auth/login", data={"username": student["email"], "password": "Test1234!"})
    token = login.json()["access_token"]
    create = client.post(
        "/offers",
        json={"title": "T", "mission": "M", "competences": "C"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 200


def test_role_change_on_unknown_user_returns_404(client, make_user):
    admin = make_user("admin")
    response = client.patch("/users/999999/role", json={"role": "company"}, headers=admin["headers"])
    assert response.status_code == 404
