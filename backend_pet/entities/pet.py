from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    age: str
    type: str
