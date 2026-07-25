import uuid

from app.db.session import SessionLocal
from app.repositories.offer_repository import OfferRepository
from app.repositories.user_repository import UserRepository


def _unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


def test_user_repository_create_and_get_by_email():
    db = SessionLocal()
    try:
        email = _unique_email("unit_user")
        user = UserRepository.create(db, email=email, password="Secret123!", full_name="Unit User", role="student")
        assert user.id is not None

        fetched = UserRepository.get_by_email(db, email)
        assert fetched is not None
        assert fetched.id == user.id
        # Le mot de passe ne doit jamais être stocké en clair.
        assert fetched.hashed_password != "Secret123!"
    finally:
        db.close()


def test_user_repository_get_by_email_returns_none_when_missing():
    db = SessionLocal()
    try:
        assert UserRepository.get_by_email(db, "does-not-exist@example.com") is None
    finally:
        db.close()


def test_offer_repository_create_defaults_to_draft():
    db = SessionLocal()
    try:
        company = UserRepository.create(db, email=_unique_email("unit_company"), password="Secret123!", full_name="Unit Co", role="company")
        offer = OfferRepository.create(db, title="T", mission="M", competences="C", company_id=company.id)
        assert offer.status == "draft"
        assert offer.company_id == company.id
    finally:
        db.close()


def test_offer_repository_update_status_persists():
    db = SessionLocal()
    try:
        company = UserRepository.create(db, email=_unique_email("unit_company"), password="Secret123!", full_name="Unit Co", role="company")
        offer = OfferRepository.create(db, title="T", mission="M", competences="C", company_id=company.id)
        updated = OfferRepository.update_status(db, offer, "submitted")
        assert updated.status == "submitted"

        refetched = OfferRepository.get_by_id(db, offer.id)
        assert refetched.status == "submitted"
    finally:
        db.close()


def test_get_active_application_ignores_rejected_and_withdrawn():
    db = SessionLocal()
    try:
        company = UserRepository.create(db, email=_unique_email("unit_company"), password="Secret123!", full_name="Unit Co", role="company")
        student = UserRepository.create(db, email=_unique_email("unit_student"), password="Secret123!", full_name="Unit St", role="student")
        offer = OfferRepository.create(db, title="T", mission="M", competences="C", company_id=company.id)

        application = OfferRepository.create_application(db, student_id=student.id, offer_id=offer.id)

        active = OfferRepository.get_active_application(db, student_id=student.id, offer_id=offer.id)
        assert active is not None
        assert active.id == application.id

        OfferRepository.update_application_status(db, application, "rejected")
        active_after_reject = OfferRepository.get_active_application(db, student_id=student.id, offer_id=offer.id)
        assert active_after_reject is None
    finally:
        db.close()


def test_get_active_application_detects_accepted_as_active():
    db = SessionLocal()
    try:
        company = UserRepository.create(db, email=_unique_email("unit_company"), password="Secret123!", full_name="Unit Co", role="company")
        student = UserRepository.create(db, email=_unique_email("unit_student"), password="Secret123!", full_name="Unit St", role="student")
        offer = OfferRepository.create(db, title="T", mission="M", competences="C", company_id=company.id)

        application = OfferRepository.create_application(db, student_id=student.id, offer_id=offer.id)
        OfferRepository.update_application_status(db, application, "accepted")

        active = OfferRepository.get_active_application(db, student_id=student.id, offer_id=offer.id)
        assert active is not None
        assert active.status == "accepted"
    finally:
        db.close()
