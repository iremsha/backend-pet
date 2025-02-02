from fastapi import APIRouter, Depends

from backend_pet.services import ShopService
from backend_pet.entities.shop import Shop, ShopPayload
from backend_pet.entities.pet import Pet


router = APIRouter(prefix="/shops", tags=["shops"])


@router.post("/")
async def create(payload: ShopPayload, service: "ShopService" = Depends(ShopService)) -> Shop:
    return await service.create(payload=payload)


@router.put("/")
async def update(payload: ShopPayload, service: "ShopService" = Depends(ShopService)) -> Shop:
    return await service.update(payload=payload)


@router.get("/{shop_id}")
async def get(shop_id: int, service: "ShopService" = Depends(ShopService)) -> Shop:
    return await service.get(shop_id=shop_id)


@router.get("/{shop_id}/pets")
async def get_pets(shop_id: int, service: "ShopService" = Depends(ShopService)) -> list[Pet]:
    return await service.get_pets(shop_id=shop_id)
