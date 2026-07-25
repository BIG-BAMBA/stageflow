from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate
from app.schemas.user import UserMe

router = APIRouter()


@router.post("/login", response_model=Token, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = UserRepository.get_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token({"sub": user.email, "role": user.role})
    return Token(access_token=token)


@router.post("/register", response_model=UserMe, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserMe:
    existing = UserRepository.get_by_email(db, str(user_data.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = UserRepository.create(db, email=str(user_data.email), password=user_data.password, full_name=user_data.full_name, role=user_data.role)
    return UserMe(id=user.id, email=user.email, full_name=user.full_name, role=user.role)