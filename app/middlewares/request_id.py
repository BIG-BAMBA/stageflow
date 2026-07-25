from starlette.requests import Request
from starlette.responses import Response


async def add_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "local")
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
