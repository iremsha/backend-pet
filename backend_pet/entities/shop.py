
from pydantic import BaseModel


class Owner(BaseModel):
    id: int
    name: str


class ShopPayload(BaseModel):
    name: str
    address: str


class Shop(BaseModel):
    id: int
    name: str
    address: str
    owner: Owner | None
