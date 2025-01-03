import uuid
from contextvars import ContextVar

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

RequestIDHeader = "X-Request-ID"

_request_id: ContextVar[str] = ContextVar("request_id")


def get_request_id() -> str:
    try:
        return _request_id.get()
    except LookupError:
        request_id = gen_request_id()
        set_request_id(request_id)
        return request_id


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def gen_request_id() -> str:
    return str(uuid.uuid4())


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp, header_key: str = RequestIDHeader):
        self.app = app
        self.header_key = header_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = Headers(scope=scope)
        request_id = headers.get(self.header_key) or gen_request_id()
        set_request_id(request_id)
        return await self.app(scope, receive, send)
