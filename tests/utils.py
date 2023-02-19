from typing import Protocol, TypeVar

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)


class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co:
        ...


class DummyAsyncIterator:
    def __init__(self, sequence: SupportsNext[_T]):
        self.sequence = sequence

    def __aiter__(self) -> "DummyAsyncIterator":
        return self

    async def __anext__(self) -> _T:
        try:
            return next(self.sequence)
        except StopIteration as e:
            raise StopAsyncIteration from e
