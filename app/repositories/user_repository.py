from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.hashing import get_password_hash


class UserRepository:
    @staticmethod
    def create(db: Session, *, email: str, password: str, full_name: str, role: str) -> User:
        user = User(email=email, hashed_password=get_password_hash(password), full_name=full_name, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_all(db: Session) -> list[User]:
        return db.query(User).order_by(User.id).all()

    @staticmethod
    def update_role(db: Session, user: User, new_role: str) -> User:
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
