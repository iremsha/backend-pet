from collections.abc import Sequence

from sqlalchemy import select

from backend_pet.models import Pet
from backend_pet.repositories.base import Repository
from backend_pet.web.core.logging import get_logger

logger = get_logger(__name__)


class PetRepository(Repository[Pet]):
    table = Pet

    async def list(self, ids: list[int]) -> Sequence[Pet]:
        logger.info(event="Getting pets by ids ...", ids=ids)
        query = select(self.table).where(self.table.id.in_(ids))

        stmt = await self.session.execute(query)
        result = stmt.scalars().all()
        logger.info(event="Got pets by ids", result=result)

        return result
