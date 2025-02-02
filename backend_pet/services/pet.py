from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend_pet.clients.e1 import E1APIClient
from backend_pet.database import get_async_session
from backend_pet.entities.pet import Pet, PetPayload
from backend_pet.repositories import PetRepository
from backend_pet.web.core.logging import get_logger

logger = get_logger(__name__)


class PetService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.pet_repo = PetRepository(session=session)
        self.e1_client = E1APIClient()

    async def get(self, pet_id: int) -> Pet:
        raise NotImplemented

    async def list(self, pet_ids: list[int] | None) -> list[Pet]:
        logger.info("Starting getting pet ...")
        result = await self.pet_repo.list(ids=pet_ids)
        logger.info(event="Result pet", result=result)

        return [Pet(id=pet.id, name=pet.name, age=pet.age, type=pet.type) for pet in result]

    async def create(self, payload: PetPayload) -> Pet:
        raise NotImplemented

    async def update(self, payload: PetPayload) -> Pet:
        raise NotImplemented