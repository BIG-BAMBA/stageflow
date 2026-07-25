from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.offer import Offer


class OfferRepository:
    @staticmethod
    def create(db: Session, *, title: str, mission: str, competences: str, company_id: int) -> Offer:
        offer = Offer(title=title, mission=mission, competences=competences, company_id=company_id, status="draft")
        db.add(offer)
        db.commit()
        db.refresh(offer)
        return offer

    @staticmethod
    def get_by_id(db: Session, offer_id: int) -> Offer | None:
        return db.query(Offer).filter(Offer.id == offer_id).first()

    @staticmethod
    def list(db: Session) -> list[Offer]:
        return db.query(Offer).all()

    @staticmethod
    def update_status(db: Session, offer: Offer, status: str) -> Offer:
        offer.status = status
        db.commit()
        db.refresh(offer)
        return offer

    @staticmethod
    def create_application(db: Session, *, student_id: int, offer_id: int) -> Application:
        application = Application(student_id=student_id, offer_id=offer_id, status="pending")
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def get_applications_for_offer(db: Session, offer_id: int):
        return db.query(Application).filter(Application.offer_id == offer_id).all()

    @staticmethod
    def get_applications_for_student(db: Session, student_id: int):
        return db.query(Application).filter(Application.student_id == student_id).all()

    @staticmethod
    def get_application_by_id(db: Session, application_id: int) -> Application | None:
        return db.query(Application).filter(Application.id == application_id).first()

    @staticmethod
    def update_application_status(db: Session, application: Application, status: str) -> Application:
        application.status = status
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def delete_application(db: Session, application: Application) -> None:
        db.delete(application)
        db.commit()
   
    @staticmethod
    def list_all_applications(db: Session) -> "list[Application]":        
        return db.query(Application).all()

    
    @staticmethod
    def get_active_application(db: Session, *, student_id: int, offer_id: int) -> Application | None:
        return db.query(Application).filter(
            Application.student_id == student_id,
            Application.offer_id == offer_id,
            Application.status.in_(["pending", "accepted"]),
        ).first()