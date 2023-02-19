import abc
from typing import Any


class Serializer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def dumps(self, payload: Any) -> bytes:
        ...

    @abc.abstractmethod
    def loads(self, data: bytes) -> Any:
        ...
