from abc import abstractmethod
from collections.abc import Coroutine

import httpx
import structlog
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette import status

from backend_pet.repositories import UniqueFieldError

logger = structlog.get_logger("ExceptionHandler")


class ErrorResponseSchema(BaseModel):
    """Describes interface for parsed API responses."""

    @abstractmethod
    def get_formatted_error_description(self) -> str:
        """Returns error description."""

    @property
    def http_status_code(self) -> int | None:
        return None


class BaseError(Exception):
    """Describes base API api_clients exception."""

    def __init__(
        self,
        *args,
        request: httpx.Request | None = None,
        response: httpx.Response | None = None,
        parsed_error: ErrorResponseSchema | None = None,
        **kwargs,
    ):
        super().__init__(*args)

        self.request = request
        self.response = response
        self.parsed_error = parsed_error

    # noinspection TaskProblemsInspection
    def __str__(self) -> str:
        if url := getattr(self.request, "url", ""):
            url = f"url={url}"

        if method := getattr(self.request, "method", ""):
            method = f"method={method}"

        if status_code := (self.response.status_code if self.response else ""):
            status_code = f"status_code={status_code}"

        if args := (",".join(self.args) if self.args else ""):
            args = f"args={args}"

        if parsed_error := (
            self.parsed_error.get_formatted_error_description() if getattr(self, "parsed_error", None) else ""
        ):
            parsed_error = f"parsed_error={parsed_error}"

        payload = "; ".join(
            filter(
                lambda x: x,
                [url, method, status_code, parsed_error, args],
            ),
        )
        return f"{self.__class__.__name__}({payload})"


class HTTPError(BaseError):
    """Describes HTTP error."""

    def __init__(
        self,
        *args,
        request: httpx.Request | None = None,
        response: httpx.Response | None = None,
        parsed_error: ErrorResponseSchema | None = None,
    ):
        super().__init__(*args, request=request, response=response)

        self.parsed_error = parsed_error


class NetworkError(BaseError):
    """Describes network errors."""


class APIProtocolError(BaseError):
    """Describes parsing response errors."""


async def unique_field_exception_handler(request: Request, exc: UniqueFieldError) -> JSONResponse:
    logger.info("Unique field error url=%s, error=%s", str(request.url), exc.detail)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.detail})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Coroutine:
    logger.info("RequestValidationError url=%s, error=%s", str(request.url), str(exc))
    return request_validation_exception_handler(request, exc)


async def http_exception_handler(request: Request, exc: HTTPError) -> JSONResponse:
    exception_class = exc.__class__.__name__
    parsed_error = exc.parsed_error
    logger.warning(
        "%s url=%s, error=%s",
        exception_class,
        str(request.url),
        str(parsed_error or exc),
    )

    response_detail = (
        parsed_error.get_formatted_error_description() if parsed_error else "Provider response validation error"
    )

    return JSONResponse(status_code=exc.response.status_code, content={"detail": response_detail})


async def network_exception_handler(request: Request, exc: NetworkError) -> JSONResponse:
    logger.warning("NetworkError url=%s, error=%s", str(request.url), str(exc))
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": "Provider network error, try again later"},
    )


async def api_protocol_exception_handler(request: Request, exc: APIProtocolError) -> JSONResponse:
    logger.exception("APIProtocolError url=%s, error=%s", str(request.url), str(exc))
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "API response parsing error"},
    )
