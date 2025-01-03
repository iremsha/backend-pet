import uuid
from collections.abc import Callable
from functools import wraps

from asyncpg import Connection
from sqlalchemy import MetaData
from sqlalchemy.ext import asyncio as sa_async
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from backend_pet.config import config

METADATA = MetaData(
    naming_convention={
        "all_column_names": lambda constraint, table: "_".join(
            [column.name for column in constraint.columns.values()],
        ),
        # A string mnemonic for primary key.
        "pk": "pk__%(table_name)s",
        # A string mnemonic for index.
        "ix": "ix__%(table_name)s__%(all_column_names)s",
        # A string mnemonic for foreign key.
        "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
        # A string mnemonic for unique constraint.
        "uq": "uq__%(table_name)s__%(all_column_names)s",
        # A string mnemonic for check constraint.
        "ck": "ck__%(table_name)s__%(constraint_name)s",
    },
)


class AsyncConnection(Connection):
    """Solved https://github.com/sqlalchemy/sqlalchemy/issues/6467."""

    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid.uuid4()}__"


def transaction(func: Callable):
    """Class method decorator to control session transaction."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        _commit = kwargs.pop("_commit", True)
        result = await func(*args, **kwargs)

        self = args[0]
        if _commit:
            await self.session.commit()
        else:
            await self.session.flush()

        return result

    return wrapper


async def get_async_session() -> sa_async.AsyncSession:
    async with async_session_maker() as session:
        yield session


engine: sa_async.AsyncEngine = sa_async.create_async_engine(
    url=str(config.postgres_dsn),
    echo=config.postgres_echo,
    echo_pool=config.postgres_echo,
    connect_args={"connection_class": AsyncConnection},
    # Because we are using "pgbouncer" for postgres (POC, PROD), disabling pooling here may
    # reduce amount of "broken connection" ConnectionDoesNotExistError errors
    poolclass=NullPool,
)

async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=sa_async.AsyncSession)

Base = declarative_base(metadata=METADATA)
