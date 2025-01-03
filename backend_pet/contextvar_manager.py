import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from contextvars import ContextVar


UNSET = object()


def get_string_uuid4() -> str:
    return str(uuid.uuid4())


class ContextVarManager:
    """Describes interface for manipulating ContextVar."""

    def __init__(
        self,
        context_var: "ContextVar",
        generator: Callable[[], str] = get_string_uuid4,
        logger=None,
    ):
        self._context = context_var
        self.generator = generator
        self.logger = logger

    def get(self, default: str | None = UNSET) -> str | None:
        try:
            return self._context.get()
        except LookupError:
            if default is not UNSET:
                return default
            raise

    def set(self, value: str) -> None:
        self._context.set(value)

    def create(self) -> str:
        new = self.generator()
        self.set(new)
        return new

    def replace(self) -> str:
        old_value = self.get(None)
        new = self.create()

        if self.logger is not None:
            self.logger.debug(f"Changed context_var_name={self._context.name} " f"from={old_value} " f"to={new}")

        return new

    def get_or_create(self) -> str:
        if (_id := self.get(None)) is not None:
            return _id
        return self.create()
