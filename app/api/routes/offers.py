from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.errors import error_responses, raise_business_error, raise_forbidden, raise_not_found
from app.core.permissions import require_authenticated_user, require_role
from app.db.session import get_db
from app.repositories.offer_repository import OfferRepository
from app.repositories.user_repository import UserRepository
from app.schemas.application import ApplicationDecision, ApplicationRead
from app.schemas.offer import OfferCreate, OfferRead, OfferReview
from app.models.offer import Offer

router = APIRouter()


@router.post(
    "/offers",
    response_model=OfferRead,
    tags=["offers"],
    summary="Créer une offre en brouillon",
    responses=error_responses(401, 403),
)
def create_offer(payload: OfferCreate, current_user: dict = Depends(require_role("company", "admin")), db: Session = Depends(get_db)) -> OfferRead:
    company_id = payload.company_id if payload.company_id is not None else current_user["id"]
    offer = OfferRepository.create(db, title=payload.title, mission=payload.mission, competences=payload.competences, company_id=company_id)
    return OfferRead(id=offer.id, title=offer.title, mission=offer.mission, competences=offer.competences, company_id=offer.company_id, status=offer.status)


@router.get("/offers/stats", response_model=dict, tags=["offers"])
def stats(current_user: dict = Depends(require_role("program_manager", "admin")), db: Session = Depends(get_db)) -> dict:
    offers = OfferRepository.list(db)
    applications = OfferRepository.list_all_applications(db)
    return {
        "offers_by_status": {status: sum(1 for offer in offers if offer.status == status) for status in ["draft", "submitted", "published", "rejected"]},
        "applications_by_status": {status: sum(1 for application in applications if application.status == status) for status in ["pending", "accepted", "rejected", "withdrawn"]},
    }


@router.get("/offers", response_model=list[OfferRead], tags=["offers"])
def list_offers(current_user: dict = Depends(require_authenticated_user), db: Session = Depends(get_db)) -> list[OfferRead]:
    offers = OfferRepository.list(db)

    def is_visible(offer: Offer) -> bool:
        if offer.status == "published":
            return True
        if current_user["role"] in {"program_manager", "admin"}:
            return True
        if current_user["role"] == "company" and offer.company_id == current_user["id"]:
            return True
        return False

    visible = [offer for offer in offers if is_visible(offer)]
    return [OfferRead(id=offer.id, title=offer.title, mission=offer.mission, competences=offer.competences, company_id=offer.company_id, status=offer.status) for offer in visible]


@router.get(
    "/offers/{offer_id}",
    response_model=OfferRead,
    tags=["offers"],
    summary="Consulter une offre",
    responses=error_responses(401, 403, 404),
)
def get_offer(offer_id: int, current_user: dict = Depends(require_authenticated_user), db: Session = Depends(get_db)) -> OfferRead:
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise_not_found("Offer not found")
    if offer.status != "published":
        if current_user["role"] == "company" and offer.company_id != current_user["id"]:
            raise_forbidden("Offer not visible")
        if current_user["role"] == "student":
            raise_forbidden("Offer not visible")
    return OfferRead(id=offer.id, title=offer.title, mission=offer.mission, competences=offer.competences, company_id=offer.company_id, status=offer.status)


@router.patch(
    "/offers/{offer_id}/submit",
    response_model=OfferRead,
    tags=["offers"],
    summary="Soumettre une offre en brouillon (draft -> submitted)",
    responses=error_responses(400, 401, 403, 404),
)
def submit_offer(offer_id: int, current_user: dict = Depends(require_role("company", "admin")), db: Session = Depends(get_db)) -> OfferRead:
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise_not_found("Offer not found")
    if offer.company_id != current_user["id"] and current_user["role"] != "admin":
        raise_forbidden("You can only submit your own offers")
    if not offer.title or not offer.mission or not offer.competences or not offer.company_id:
        raise_business_error("Title, mission, competences and company are required")
    if offer.status != "draft":
        raise_business_error("Offer status transition must be explicit")
    offer = OfferRepository.update_status(db, offer, "submitted")
    return OfferRead(id=offer.id, title=offer.title, mission=offer.mission, competences=offer.competences, company_id=offer.company_id, status=offer.status)


@router.patch(
    "/offers/{offer_id}/review",
    response_model=OfferRead,
    tags=["offers"],
    summary="Publier ou refuser une offre soumise (réservé au responsable pédagogique)",
    responses=error_responses(400, 401, 403, 404),
)
def review_offer(offer_id: int, payload: OfferReview, current_user: dict = Depends(require_role("program_manager", "admin")), db: Session = Depends(get_db)) -> OfferRead:
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise_not_found("Offer not found")
    if offer.status != "submitted":
        raise_business_error("Offer status transition must be explicit")
    if payload.decision not in {"publish", "reject"}:
        raise_business_error("Decision must be publish or reject")
    if payload.decision == "publish":
        if not offer.title or not offer.mission or not offer.competences or not offer.company_id:
            raise_business_error("Offer cannot be published without title, mission, competences and company")
        offer = OfferRepository.update_status(db, offer, "published")
    else:
        offer = OfferRepository.update_status(db, offer, "rejected")
    return OfferRead(id=offer.id, title=offer.title, mission=offer.mission, competences=offer.competences, company_id=offer.company_id, status=offer.status)


@router.post(
    "/offers/{offer_id}/applications",
    response_model=ApplicationRead,
    tags=["offers"],
    summary="Déposer une candidature sur une offre publiée",
    responses=error_responses(400, 401, 403, 404),
)
def create_application(offer_id: int, current_user: dict = Depends(require_role("student", "admin")), db: Session = Depends(get_db)) -> ApplicationRead:
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise_not_found("Offer not found")
    if offer.status != "published":
        raise_business_error("Offer is not published")
    existing = OfferRepository.get_active_application(db, student_id=current_user["id"], offer_id=offer_id)
    if existing:
        raise_business_error("A student can only have one active application per offer")
    application = OfferRepository.create_application(db, student_id=current_user["id"], offer_id=offer_id)
    return ApplicationRead(id=application.id, student_id=application.student_id, offer_id=application.offer_id, status=application.status)


@router.get("/applications/me", response_model=list[ApplicationRead], tags=["offers"])
def my_applications(current_user: dict = Depends(require_role("student", "company", "program_manager", "admin")), db: Session = Depends(get_db)) -> list[ApplicationRead]:
    applications = OfferRepository.get_applications_for_student(db, current_user["id"])
    return [ApplicationRead(id=application.id, student_id=application.student_id, offer_id=application.offer_id, status=application.status) for application in applications]


@router.get(
    "/offers/{offer_id}/applications",
    response_model=list[ApplicationRead],
    tags=["offers"],
    summary="Lister les candidatures d'une offre (entreprise propriétaire, responsable ou admin)",
    responses=error_responses(401, 403, 404),
)
def list_offer_applications(offer_id: int, current_user: dict = Depends(require_authenticated_user), db: Session = Depends(get_db)) -> list[ApplicationRead]:
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise_not_found("Offer not found")
    if current_user["role"] == "company" and offer.company_id != current_user["id"]:
        raise_forbidden("Company cannot access other company applications")
    if current_user["role"] not in {"company", "program_manager", "admin"}:
        raise_forbidden("Forbidden")
    applications = OfferRepository.get_applications_for_offer(db, offer_id)
    return [ApplicationRead(id=application.id, student_id=application.student_id, offer_id=application.offer_id, status=application.status) for application in applications]


@router.patch(
    "/applications/{application_id}/decision",
    response_model=ApplicationRead,
    tags=["offers"],
    summary="Accepter, refuser ou retirer une candidature (réservé au responsable pédagogique)",
    responses=error_responses(400, 401, 403, 404),
)
def decide_application(application_id: int, payload: ApplicationDecision, current_user: dict = Depends(require_role("program_manager", "admin")), db: Session = Depends(get_db)) -> ApplicationRead:
    application = OfferRepository.get_application_by_id(db, application_id)
    if not application:
        raise_not_found("Application not found")
    if payload.decision not in {"accepted", "rejected", "withdrawn"}:
        raise_business_error("Decision must be accepted, rejected or withdrawn")
    application = OfferRepository.update_application_status(db, application, payload.decision)
    return ApplicationRead(id=application.id, student_id=application.student_id, offer_id=application.offer_id, status=application.status)


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["offers"],
    summary="Retirer sa propre candidature tant qu'elle est en attente",
    responses=error_responses(400, 401, 403, 404),
)
def delete_application(application_id: int, current_user: dict = Depends(require_role("student", "admin")), db: Session = Depends(get_db)) -> None:
    application = OfferRepository.get_application_by_id(db, application_id)
    if not application:
        raise_not_found("Application not found")
    if application.student_id != current_user["id"] and current_user["role"] != "admin":
        raise_forbidden("You can only delete your own applications")
    if application.status != "pending":
        raise_business_error("Accepted applications cannot be deleted")
    OfferRepository.delete_application(db, application)
