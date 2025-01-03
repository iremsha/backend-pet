import logging
import sys
from collections.abc import Sequence
from typing import Any

import structlog
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, bound_contextvars, clear_contextvars
from structlog.typing import EventDict

from backend_pet.web.core.request_id import get_request_id

__all__ = (
    "LoggingMiddleware",
    "configure_logging",
    "get_logger",
    "bind_contextvars",
    "bound_contextvars",
)


def get_logger(name: str, *args: tuple[Any], **kwargs: dict[str, Any]) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name, *args, **kwargs)


logger = get_logger(__name__)


def configure_logging(*, level: str, disable_existing_loggers: bool = True) -> None:
    if disable_existing_loggers:
        for name in logging.root.manager.loggerDict:
            if not name.startswith("uvicorn"):
                logging.getLogger(name).propagate = False

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )
    structlog.configure(
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            *get_caller_processor(),
            structlog.processors.EventRenamer(to="message"),
            structlog.processors.JSONRenderer(),
        ],
    )


def get_caller_processor() -> list:
    callers = structlog.processors.CallsiteParameter

    def _caller_processor(_, __, event_dict: EventDict) -> EventDict:
        file = event_dict.pop(callers.MODULE.value)
        func = event_dict.pop(callers.FUNC_NAME.value)
        line = event_dict.pop(callers.LINENO.value)
        event_dict["caller"] = f"{file}.{func}:{line}"
        return event_dict

    return [
        structlog.processors.CallsiteParameterAdder({callers.MODULE, callers.FUNC_NAME, callers.LINENO}),
        _caller_processor,
    ]


class LoggingMiddleware:
    def __init__(self, app: ASGIApp, skip_paths: Sequence[str] = ()):
        self.app = app
        self.skip_paths = set(skip_paths)
        self.log_config = {
            200: {
                "level": logging.INFO,
                "message": "Success",
            },
            400: {
                "level": logging.INFO,
                "message": "Client error",
            },
            500: {
                "level": logging.WARNING,
                "message": "Server error",
            },
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive, send)
        if request.url.path in self.skip_paths:
            return await self.app(scope, receive, send)

        bind_contextvars(request_id=get_request_id())

        query_params = str(request.query_params)
        request_body, wrapped_receive = await self.receive_body(receive)
        status_code = 500
        response_body = b""
        exc_info = None

        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                nonlocal status_code
                status_code = message["status"]
            elif message["type"] == "http.response.body" and message["body"]:
                nonlocal response_body
                response_body += message["body"]
            await send(message)

        try:
            return await self.app(scope, wrapped_receive, wrapped_send)
        except Exception as e:
            exc_info = e
            raise
        finally:
            config = self.log_config[200]
            if status_code >= 500:
                config = self.log_config[500]
            elif status_code >= 400:
                config = self.log_config[400]

            logger.log(
                config["level"],
                config["message"],
                method=request.method,
                path=request.url.path,
                query_params=query_params,
                request_body=request_body,
                status_code=status_code,
                response_body=response_body,
                exc_info=exc_info,
            )
            clear_contextvars()

    # from Elastic contrib:
    # https://github.com/elastic/apm-agent-python/blob/515df75ab75163912411de419564753a0d38b0c3/elasticapm/contrib/asgi.py
    @staticmethod
    async def receive_body(receive: Receive) -> tuple[bytes, Receive]:
        messages = []
        more_body = True
        while more_body:
            message = await receive()
            messages.append(message)
            more_body = message.get("more_body", False)
        request_body = b"".join([message.get("body", b"") for message in messages])

        async def wrapped_receive() -> Message:
            if messages:
                return messages.pop(0)
            return await receive()

        return request_body, wrapped_receive
