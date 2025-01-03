from fastapi import APIRouter, Depends

from backend_pet.entities.pet import Pet
from backend_pet.services import PetService

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/")
async def get(pet_ids: list[int], service: "PetService" = Depends(PetService)) -> list[Pet]:
    return await service.list(pet_ids=pet_ids)
