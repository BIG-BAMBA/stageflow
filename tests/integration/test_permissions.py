def test_unauthenticated_user_cannot_create_offer(client):
    response = client.post("/offers", json={"title": "T", "mission": "M", "competences": "C"})
    assert response.status_code == 401


def test_student_cannot_create_offer(client, make_user):
    student = make_user("student")
    response = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=student["headers"]
    )
    assert response.status_code == 403


def test_company_cannot_review_offer(client, make_user):
    company = make_user("company")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]
    client.patch(f"/offers/{offer_id}/submit", headers=company["headers"])

    response = client.patch(
        f"/offers/{offer_id}/review", json={"decision": "publish"}, headers=company["headers"]
    )
    assert response.status_code == 403


def test_student_cannot_review_offer(client, make_user):
    company = make_user("company")
    student = make_user("student")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]
    client.patch(f"/offers/{offer_id}/submit", headers=company["headers"])

    response = client.patch(
        f"/offers/{offer_id}/review", json={"decision": "publish"}, headers=student["headers"]
    )
    assert response.status_code == 403


def test_program_manager_can_publish_offer(client, make_user):
    company = make_user("company")
    manager = make_user("program_manager")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]
    client.patch(f"/offers/{offer_id}/submit", headers=company["headers"])

    response = client.patch(
        f"/offers/{offer_id}/review", json={"decision": "publish"}, headers=manager["headers"]
    )
    assert response.status_code == 200
    assert response.json()["status"] == "published"


def test_student_cannot_decide_on_application(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    application = client.post(f"/offers/{offer_id}/applications", headers=student["headers"]).json()
    response = client.patch(
        f"/applications/{application['id']}/decision",
        json={"decision": "accepted"},
        headers=student["headers"],
    )
    assert response.status_code == 403


def test_stats_forbidden_for_student_and_company(client, make_user):
    student = make_user("student")
    company = make_user("company")

    for user in (student, company):
        response = client.get("/offers/stats", headers=user["headers"])
        assert response.status_code == 403


def test_stats_allowed_for_program_manager(client, make_user):
    manager = make_user("program_manager")
    response = client.get("/offers/stats", headers=manager["headers"])
    assert response.status_code == 200
    body = response.json()
    assert "offers_by_status" in body
    assert "applications_by_status" in body
