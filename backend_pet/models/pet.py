import sqlalchemy as sa
import sqlalchemy.orm as so

from backend_pet.database import Base
from models.common import HasTimestamp


class Pet(Base, HasTimestamp):
    __tablename__ = "pets"

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str]
    age: so.Mapped[int]
    type: so.Mapped[str]

    def __repr__(self) -> str:
        return f"<Pet {self.id=} {self.type=} {self.name=}>"
