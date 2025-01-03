import sentry_sdk
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from starlette.types import ASGIApp, Receive, Scope, Send

from backend_pet.config import config
from backend_pet.web.core.request_id import get_request_id


def initial_sentry() -> None:
    if config.sentry_dsn:
        sentry_sdk.init(
            dsn=str(config.sentry_dsn),
            environment=config.environment,
            traces_sample_rate=0.1,
            integrations=[
                LoggingIntegration(),
                HttpxIntegration(),
            ],
            max_breadcrumbs=300,
        )


class SentryMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id = get_request_id()
        sentry_sdk.set_tag("request_id", request_id)
        sentry_sdk.set_tag("transaction_id", request_id)
        return await self.app(scope, receive, send)
