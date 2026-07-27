from __future__ import annotations
from typing import Any
from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, field_errors: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field_errors = field_errors or {}
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, code: str = "NOT_FOUND", message: str = "Resource tidak ditemukan"):
        super().__init__(code, message, 404)


class ConflictError(AppError):
    def __init__(self, code: str = "CONFLICT", message: str = "Konflik data"):
        super().__init__(code, message, 409)


class ValidationError(AppError):
    def __init__(self, code: str = "VALIDATION_ERROR", message: str = "Validasi gagal", field_errors: dict | None = None):
        super().__init__(code, message, 422, field_errors)


def _error_body(code: str, message: str, request_id: str, field_errors: dict | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message, "requestId": request_id}
    if field_errors:
        body["fieldErrors"] = field_errors
    return body


def _get_req_id(request: Request) -> str:
    return request.state.request_id if hasattr(request.state, "request_id") else "unknown"


async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, _get_req_id(request), exc.field_errors or None),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=_error_body("HTTP_ERROR", str(exc.detail), _get_req_id(request)),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    field_errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = ".".join(str(l) for l in err["loc"] if l not in ("body", "query"))
        field_errors.setdefault(loc, []).append(err["msg"])
    return ORJSONResponse(
        status_code=422,
        content=_error_body("VALIDATION_ERROR", "Validasi gagal", _get_req_id(request), field_errors),
    )


async def generic_error_handler(request: Request, exc: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=500,
        content=_error_body("INTERNAL_ERROR", "Terjadi kesalahan internal", _get_req_id(request)),
    )
