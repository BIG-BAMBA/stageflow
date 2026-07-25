from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user


def require_role(*allowed_roles: str):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user

    return dependency


def require_authenticated_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user
