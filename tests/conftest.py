import os
import sys
import uuid
from pathlib import Path

# IMPORTANT: ces variables d'environnement doivent être fixées AVANT d'importer
# quoi que ce soit de `app`, sinon app.core.config.settings aura déjà lu
# la configuration de développement (et donc pointerait vers la vraie DB).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_stageflow.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-please-change")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    """Crée un schéma propre une seule fois pour toute la session de tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def make_user(client):
    """Factory: crée un utilisateur avec un rôle donné, le connecte,
    et retourne son id, son email et ses headers d'autorisation prêts à l'emploi.
    """

    def _make_user(role: str, password: str = "Test1234!"):
        email = f"{role}_{uuid.uuid4().hex[:10]}@example.com"
        register = client.post(
            "/auth/register",
            json={"email": email, "password": password, "full_name": f"{role.title()} Test", "role": role},
        )
        assert register.status_code == 201, register.text        
        user_id = register.json()["id"]

        login = client.post("/auth/login", data={"username": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]

        return {"id": user_id, "email": email, "role": role, "headers": {"Authorization": f"Bearer {token}"}}

    return _make_user


@pytest.fixture()
def publish_offer(client):
    """Helper: crée une offre pour une entreprise donnée et la fait passer
    par tout le cycle draft -> submitted -> published.
    """

    def _publish(company_headers: dict, manager_headers: dict, title="Stage Test", mission="Mission test", competences="Python"):
        create = client.post(
            "/offers",
            json={"title": title, "mission": mission, "competences": competences},
            headers=company_headers,
        )
        assert create.status_code == 200, create.text
        offer_id = create.json()["id"]

        submit = client.patch(f"/offers/{offer_id}/submit", headers=company_headers)
        assert submit.status_code == 200, submit.text

        review = client.patch(f"/offers/{offer_id}/review", json={"decision": "publish"}, headers=manager_headers)
        assert review.status_code == 200, review.text

        return offer_id

    return _publish
