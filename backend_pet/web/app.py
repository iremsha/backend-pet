from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from backend_pet.config import config
from backend_pet.repositories import UniqueFieldError
from web.core.exception_handlers import (
    APIProtocolError,
    HTTPError,
    NetworkError,
    api_protocol_exception_handler,
    http_exception_handler,
    network_exception_handler,
    unique_field_exception_handler,
    validation_exception_handler,
)
from backend_pet.web.core.logging import LoggingMiddleware, configure_logging
from backend_pet.web.core.request_id import RequestIDMiddleware
from backend_pet.web.core.sentry import SentryMiddleware, initial_sentry
from backend_pet.web.routes import metrics_router, v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        debug=config.debug,
        title=config.title,
        description=config.description,
        version="0.1.4",
    )

    initial_sentry()
    configure_logging(level=config.log_level)

    add_exception_handlers(app)
    add_middlewares(app)
    include_routers(app)

    return app


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        app_name="backend_pet",
        skip_paths=["/healthz", "/metrics"],
        group_paths=True,
    )
    app.add_middleware(
        LoggingMiddleware,
        skip_paths=["/healthz", "/metrics"],
    )
    app.add_middleware(SentryMiddleware)
    app.add_middleware(RequestIDMiddleware)


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UniqueFieldError, unique_field_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPError, http_exception_handler)
    app.add_exception_handler(NetworkError, network_exception_handler)
    app.add_exception_handler(APIProtocolError, api_protocol_exception_handler)


def include_routers(app: FastAPI) -> None:
    app.include_router(v1_router)
    app.include_router(metrics_router)
