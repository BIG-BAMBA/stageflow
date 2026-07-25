def test_offer_cannot_be_reviewed_before_submission(client, make_user):
    company = make_user("company")
    manager = make_user("program_manager")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]

    response = client.patch(
        f"/offers/{offer_id}/review", json={"decision": "publish"}, headers=manager["headers"]
    )
    assert response.status_code == 400


def test_offer_cannot_be_submitted_twice(client, make_user):
    company = make_user("company")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]

    first = client.patch(f"/offers/{offer_id}/submit", headers=company["headers"])
    assert first.status_code == 200

    second = client.patch(f"/offers/{offer_id}/submit", headers=company["headers"])
    assert second.status_code == 400


def test_company_cannot_submit_another_companys_offer(client, make_user):
    company_a = make_user("company")
    company_b = make_user("company")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company_a["headers"]
    )
    offer_id = create.json()["id"]

    response = client.patch(f"/offers/{offer_id}/submit", headers=company_b["headers"])
    assert response.status_code == 403


def test_student_cannot_apply_twice_while_application_is_pending(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    first = client.post(f"/offers/{offer_id}/applications", headers=student["headers"])
    assert first.status_code == 200

    second = client.post(f"/offers/{offer_id}/applications", headers=student["headers"])
    assert second.status_code == 400


def test_student_can_reapply_after_rejection(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    first = client.post(f"/offers/{offer_id}/applications", headers=student["headers"])
    application_id = first.json()["id"]

    reject = client.patch(
        f"/applications/{application_id}/decision", json={"decision": "rejected"}, headers=manager["headers"]
    )
    assert reject.status_code == 200

    second = client.post(f"/offers/{offer_id}/applications", headers=student["headers"])
    assert second.status_code == 200
    assert second.json()["status"] == "pending"


def test_student_cannot_apply_to_a_draft_offer(client, make_user):
    company = make_user("company")
    student = make_user("student")
    create = client.post(
        "/offers", json={"title": "T", "mission": "M", "competences": "C"}, headers=company["headers"]
    )
    offer_id = create.json()["id"]

    response = client.post(f"/offers/{offer_id}/applications", headers=student["headers"])
    assert response.status_code == 400


def test_accepted_application_cannot_be_deleted_by_student(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    application = client.post(f"/offers/{offer_id}/applications", headers=student["headers"]).json()
    client.patch(
        f"/applications/{application['id']}/decision", json={"decision": "accepted"}, headers=manager["headers"]
    )

    response = client.delete(f"/applications/{application['id']}", headers=student["headers"])
    assert response.status_code == 400


def test_pending_application_can_be_deleted_by_its_owner(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    application = client.post(f"/offers/{offer_id}/applications", headers=student["headers"]).json()
    response = client.delete(f"/applications/{application['id']}", headers=student["headers"])
    assert response.status_code == 204


def test_student_cannot_delete_another_students_application(client, make_user, publish_offer):
    company = make_user("company")
    manager = make_user("program_manager")
    student_a = make_user("student")
    student_b = make_user("student")
    offer_id = publish_offer(company["headers"], manager["headers"])

    application = client.post(f"/offers/{offer_id}/applications", headers=student_a["headers"]).json()
    response = client.delete(f"/applications/{application['id']}", headers=student_b["headers"])
    assert response.status_code == 403
