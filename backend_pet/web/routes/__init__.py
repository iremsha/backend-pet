from fastapi import APIRouter

from .metrics import router as metrics_router
from .v1 import pet_router, shop_router


v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(pet_router)
v1_router.include_router(shop_router)


__all__ = [
    "v1_router",
    "metrics_router",
]
