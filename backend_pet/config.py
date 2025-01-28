from functools import cached_property

from pydantic import HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # app
    debug: bool = False
    title: str = "backend-pet"
    description: str = "Something useful"
    environment: str | None = "DEV"

    # db
    postgres_dsn: PostgresDsn = None
    postgres_echo: bool = False

    # sentry
    sentry_dsn: HttpUrl | None = None

    # client
    e1_endpoint: str = "http://e1-api.ru"
    e1_token: str = "backend_pet_test"

    # pydantic
    model_config = SettingsConfigDict(frozen=True, env_file=".env")

    @cached_property
    def log_level(self) -> str:
        return "DEBUG" if self.debug else "INFO"

    @field_validator("postgres_dsn")
    def postgres_dsn_asyncpg_scheme(cls, value: PostgresDsn) -> PostgresDsn:
        query = value.query
        if query is None:
            query = "prepared_statement_cache_size=0"
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            hosts=value.hosts(),
            path=value.path.replace("/", ""),
            query=query,
            fragment=value.fragment,
        )


config = Config()
