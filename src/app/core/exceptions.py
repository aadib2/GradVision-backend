"""Map HTTP and validation errors to the GradVision ErrorResponse shape."""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _error_body(message: str) -> dict:
    return {"success": False, "error": message}


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
    else:
        message = str(detail)
    return JSONResponse(status_code=exc.status_code, content=_error_body(message), headers=exc.headers)


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    parts: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()) if x != "body")
        msg = err.get("msg", "Invalid value")
        parts.append(f"{loc}: {msg}" if loc else msg)
    message = "; ".join(parts) if parts else "Validation error"
    return JSONResponse(
        status_code=422,
        content=_error_body(message),
    )
