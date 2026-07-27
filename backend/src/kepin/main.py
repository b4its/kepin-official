from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from kepin.core.config import get_settings
from kepin.api.middleware import RequestIDMiddleware
from kepin.api.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_error_handler,
)
from kepin.api.router import api_router
from kepin.db.session import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = app
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    app.include_router(api_router)
    return app


app = create_app()
