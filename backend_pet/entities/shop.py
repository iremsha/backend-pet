from datetime import datetime

from pydantic import BaseModel


# схема для получения объектов на создание
class ShopPayload(BaseModel):
    name: str
    address: str
    owner: str

# схема для возвращения объекта
class Shop(BaseModel):
    id: int
    name: str
    address: str
    owner: str

