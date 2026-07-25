import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import raise_not_found
from app.core.permissions import require_authenticated_user, require_role
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserMe, UserRead, UserRoleUpdate

logger = logging.getLogger("stageflow.admin")

router = APIRouter()


@router.get("/me", response_model=UserMe, tags=["users"])
def get_me(current_user: dict = Depends(require_authenticated_user)) -> UserMe:
    return UserMe(id=current_user["id"], email=current_user["email"], full_name=current_user["full_name"], role=current_user["role"])


@router.get(
    "",
    response_model=list[UserRead],
    tags=["users"],
    summary="Lister tous les utilisateurs (admin uniquement)",
)
def list_users(current_user: dict = Depends(require_role("admin")), db: Session = Depends(get_db)) -> list[UserRead]:
    users = UserRepository.list_all(db)
    return [UserRead(id=u.id, email=u.email, full_name=u.full_name, role=u.role) for u in users]


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    tags=["users"],
    summary="Forcer le changement de rôle d'un utilisateur (admin uniquement)",
)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserRead:
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise_not_found("User not found")

    previous_role = user.role
    updated = UserRepository.update_role(db, user, payload.role)

    logger.info(
        "Role change: admin_id=%s admin_email=%s target_user_id=%s target_email=%s %s -> %s",
        current_user["id"], current_user["email"], updated.id, updated.email, previous_role, updated.role,
    )

    return UserRead(id=updated.id, email=updated.email, full_name=updated.full_name, role=updated.role)
