from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend_pet.database import get_async_session

AsyncSessionDepend = Annotated[AsyncSession, Depends(get_async_session)]
