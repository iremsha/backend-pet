from pydantic import BaseModel


class Pet(BaseModel):
    id: int
    name: str
    age: int
    type: str

class PetPayload(BaseModel):
    name: str
    age: int
    type: str
