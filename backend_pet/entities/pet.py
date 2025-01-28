from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    age: int
    type: str
