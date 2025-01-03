from tenacity import RetryCallState, retry, stop_after_attempt
from web.core.logging import get_logger

from backend_pet.config import config
from healpers import HTTPClient

from .entities import Info

logger = get_logger(__name__)


def log_before_sleep(retry_state: RetryCallState) -> None:
    logger.info(
        event="Retrying",
        func=retry_state.fn,
        attempt_number=retry_state.attempt_number,
        outcome=retry_state.outcome,
    )


class E1APIClient(HTTPClient):
    base_url = config.e1_endpoint
    default_headers = {"X-Token": config.e1_token}

    @retry(stop=stop_after_attempt(3), before_sleep=log_before_sleep)
    async def ping(self) -> list[Info]:
        logger.info(event="Requesting info from E1 API")
        response = await self.get(url="/api/v1/info")
        logger.info(event="Get response from E1 API", response=response)

        return [self._parse_response(info, Info) for info in response.json()]
