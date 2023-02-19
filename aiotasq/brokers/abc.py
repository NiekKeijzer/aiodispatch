import abc
from collections.abc import AsyncGenerator
from typing import Any


class Broker(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def publish(self, key: str, payload: bytes) -> None:
        ...

    @abc.abstractmethod
    async def subscribe(self, key: str) -> AsyncGenerator[bytes, Any]:
        # trick mypy into accepting this is a generator
        yield b""
