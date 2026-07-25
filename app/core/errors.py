from fastapi import HTTPException, status


def raise_business_error(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def raise_not_found(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def raise_forbidden(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


# Blocs de réponses réutilisables pour documenter les erreurs possibles dans OpenAPI/Swagger.
ERROR_400 = {400: {"description": "Règle métier invalide", "content": {"application/json": {"example": {"detail": "..."}}}}}
ERROR_401 = {401: {"description": "Non authentifié", "content": {"application/json": {"example": {"detail": "Invalid authentication credentials"}}}}}
ERROR_403 = {403: {"description": "Non habilité pour cette action", "content": {"application/json": {"example": {"detail": "Forbidden"}}}}}
ERROR_404 = {404: {"description": "Ressource absente ou non visible", "content": {"application/json": {"example": {"detail": "Not found"}}}}}


def error_responses(*codes: int) -> dict:
    """Compose un dict `responses=` FastAPI à partir des codes d'erreur pertinents pour une route."""
    mapping = {400: ERROR_400, 401: ERROR_401, 403: ERROR_403, 404: ERROR_404}
    merged: dict = {}
    for code in codes:
        merged.update(mapping[code])
    return merged
