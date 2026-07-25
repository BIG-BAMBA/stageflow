from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.offers import router as offers_router
from app.core.config import settings
from app.middlewares.request_id import add_request_id_middleware
from app.middlewares.security_headers import add_security_headers_middleware

app = FastAPI(title="StageFlow API", version="1.0.0", description="Secure internship management workflow")

app.middleware("http")(add_request_id_middleware)
app.middleware("http")(add_security_headers_middleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(offers_router, tags=["offers"])


@app.get("/")
def root():
    return {"message": "StageFlow API is running", "docs": "/docs"}