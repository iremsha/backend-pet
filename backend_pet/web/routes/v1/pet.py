from fastapi import APIRouter, Depends

from backend_pet.entities.pet import Pet, PetPayload
from backend_pet.services import PetService

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/{pet_id}")
async def get(pet_id: int, service: "PetService" = Depends(PetService)) -> Pet:
    return await service.get(pet_id=pet_id)

@router.get("/")
async def get_list(service: "PetService" = Depends(PetService)) -> list[Pet]:
    return await service.list(pet_ids=None)

@router.post("/")
async def create(payload: PetPayload, service: "PetService" = Depends(PetService)) -> Pet:
    return await service.create(payload=payload)

@router.put("/")
async def update(payload: PetPayload, service: "PetService" = Depends(PetService)) -> Pet:
    return await service.update(payload=payload)