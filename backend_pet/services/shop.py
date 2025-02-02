from backend_pet.entities.shop import Shop, ShopPayload
from backend_pet.entities.pet import Pet
from backend_pet.web.core.logging import get_logger

logger = get_logger(__name__)


class ShopService:
    async def get(self, shop_id: int) -> Shop:
        raise NotImplemented

    async def create(self, payload: ShopPayload) -> Shop:
        raise NotImplemented

    async def update(self, payload: ShopPayload) -> Shop:
        raise NotImplemented

    async def get_pets(self, shop_id: int) -> list[Pet]:
        raise NotImplemented
