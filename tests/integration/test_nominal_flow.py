def test_full_nominal_flow(client, make_user):
    """Parcours complet exigé par le sujet : une entreprise crée une offre,
    la soumet, un responsable la publie, un étudiant la consulte, candidate,
    l'entreprise voit la candidature, le responsable l'accepte, et les
    statistiques reflètent bien l'état final.
    """
    company = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")

    create = client.post(
        "/offers",
        json={
            "title": "Stage Data Engineer",
            "mission": "Construire des pipelines de données",
            "competences": "Python, Airflow, SQL",
        },
        headers=company["headers"],
    )
    assert create.status_code == 200
    offer = create.json()
    assert offer["status"] == "draft"

    submit = client.patch(f"/offers/{offer['id']}/submit", headers=company["headers"])
    assert submit.status_code == 200
    assert submit.json()["status"] == "submitted"

    review = client.patch(
        f"/offers/{offer['id']}/review", json={"decision": "publish"}, headers=manager["headers"]
    )
    assert review.status_code == 200
    assert review.json()["status"] == "published"

    listing = client.get("/offers", headers=student["headers"])
    assert listing.status_code == 200
    assert any(o["id"] == offer["id"] for o in listing.json())

    application = client.post(f"/offers/{offer['id']}/applications", headers=student["headers"])
    assert application.status_code == 200
    assert application.json()["status"] == "pending"
    application_id = application.json()["id"]

    my_applications = client.get("/applications/me", headers=student["headers"])
    assert my_applications.status_code == 200
    assert any(a["id"] == application_id for a in my_applications.json())

    company_view = client.get(f"/offers/{offer['id']}/applications", headers=company["headers"])
    assert company_view.status_code == 200
    assert len(company_view.json()) == 1

    decision = client.patch(
        f"/applications/{application_id}/decision",
        json={"decision": "accepted"},
        headers=manager["headers"],
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "accepted"

    stats = client.get("/offers/stats", headers=manager["headers"])
    assert stats.status_code == 200
    body = stats.json()
    assert body["offers_by_status"]["published"] >= 1
    assert body["applications_by_status"]["accepted"] >= 1
