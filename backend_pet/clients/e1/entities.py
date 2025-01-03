from datetime import datetime

from pydantic import BaseModel


class Info(BaseModel):
    title: str
    description: str
    created_at: datetime
