from fastapi import APIRouter, Depends
from app.core.permissions import require_authenticated_user
from app.schemas.user import UserMe

router = APIRouter()


@router.get("/me", response_model=UserMe, tags=["users"])
def get_me(current_user: dict = Depends(require_authenticated_user)) -> UserMe:
    return UserMe(id=current_user["id"], email=current_user["email"], full_name=current_user["full_name"], role=current_user["role"])
