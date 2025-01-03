from alembic import context
from sqlalchemy import engine_from_config, pool

# To configure environment-specific migration options.
from backend_pet.config import config as global_config
from backend_pet.database import Base
from backend_pet.models import *  # resolve empty migration problem


# noinspection TaskProblemsInspection


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Uses default structlog logger
# fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support.
target_metadata = Base.metadata


def update_configs():
    # не охота было ради одних миграций в конфиг добавлять другой тип подключения
    url = str(global_config.postgres_dsn).replace("+asyncpg", "").replace("?prepared_statement_cache_size=0", "")
    if not url:
        raise RuntimeError("Invalid POSTGRES DSN in migrations")
    config.set_main_option("sqlalchemy.url", url)


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
            compare_server_default=True,
            compare_type=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            if target_metadata.schema:
                context.execute(f'SET search_path TO "{target_metadata.schema}"')
            context.run_migrations()


update_configs()

run_migrations_online()
