def test_company_cannot_list_applications_of_an_offer_it_does_not_own(client, make_user, publish_offer):
    """Test d'isolation explicitement demandé par le sujet :
    une entreprise ne doit jamais pouvoir consulter les candidatures
    d'une offre appartenant à une autre entreprise.
    """
    company_a = make_user("company")
    company_b = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")

    offer_id = publish_offer(company_a["headers"], manager["headers"])
    client.post(f"/offers/{offer_id}/applications", headers=student["headers"])

    response = client.get(f"/offers/{offer_id}/applications", headers=company_b["headers"])
    assert response.status_code == 403


def test_company_owner_can_list_its_own_offer_applications(client, make_user, publish_offer):
    company_a = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")

    offer_id = publish_offer(company_a["headers"], manager["headers"])
    client.post(f"/offers/{offer_id}/applications", headers=student["headers"])

    response = client.get(f"/offers/{offer_id}/applications", headers=company_a["headers"])
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_company_does_not_see_other_companys_draft_offer_in_listing(client, make_user):
    company_a = make_user("company")
    company_b = make_user("company")

    draft = client.post(
        "/offers", json={"title": "Secret", "mission": "M", "competences": "C"}, headers=company_a["headers"]
    )
    offer_id = draft.json()["id"]

    listing = client.get("/offers", headers=company_b["headers"])
    assert listing.status_code == 200
    ids = [offer["id"] for offer in listing.json()]
    assert offer_id not in ids


def test_company_cannot_fetch_other_companys_draft_offer_directly(client, make_user):
    company_a = make_user("company")
    company_b = make_user("company")

    draft = client.post(
        "/offers", json={"title": "Secret", "mission": "M", "competences": "C"}, headers=company_a["headers"]
    )
    offer_id = draft.json()["id"]

    response = client.get(f"/offers/{offer_id}", headers=company_b["headers"])
    assert response.status_code == 403


def test_company_can_still_see_its_own_draft_offer(client, make_user):
    company_a = make_user("company")

    draft = client.post(
        "/offers", json={"title": "Mine", "mission": "M", "competences": "C"}, headers=company_a["headers"]
    )
    offer_id = draft.json()["id"]

    response = client.get(f"/offers/{offer_id}", headers=company_a["headers"])
    assert response.status_code == 200


def test_published_offer_is_visible_to_everyone(client, make_user, publish_offer):
    company_a = make_user("company")
    company_b = make_user("company")
    manager = make_user("program_manager")
    student = make_user("student")

    offer_id = publish_offer(company_a["headers"], manager["headers"])

    for viewer in (company_b, student):
        response = client.get(f"/offers/{offer_id}", headers=viewer["headers"])
        assert response.status_code == 200
