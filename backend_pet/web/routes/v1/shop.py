from fastapi import APIRouter, Depends

from backend_pet.services import ShopService
from backend_pet.entities.shop import Shop, ShopPayload

router = APIRouter(prefix="/shops", tags=["shops"])


@router.post("/")
async def get(payload: ShopPayload, service: "ShopService" = Depends(ShopService)) -> Shop:
    return await service.create(payload=payload)


@router.get("/{shop_id}")
async def get(shop_id: int, service: "ShopService" = Depends(ShopService)) -> Shop:
    return await service.get(shop_id=shop_id)
