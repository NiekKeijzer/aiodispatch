import asyncio
import dataclasses
from collections.abc import Awaitable
from types import FunctionType
from typing import Any, Callable, Optional, TypedDict, TypeVar

from .enums import Route
from .exceptions import AlreadyDoneException
from .utils import dump_attribute, generate_uuid, load_attribute


class TaskDict(TypedDict):
    function: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    route: str
    id: str


_T_DONE = TypeVar("_T_DONE")


@dataclasses.dataclass
class Task:
    function: Callable[[Any, Any], Any] | Callable[[], Awaitable[Any]]
    args: tuple[Any, ...] = dataclasses.field(default_factory=tuple)
    kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)
    route: Route = Route.TASKS
    id: str = dataclasses.field(default_factory=generate_uuid)
    timeout: Optional[float] = None

    result: Any = None
    _result_event: asyncio.Event = dataclasses.field(
        init=False, default_factory=asyncio.Event
    )
    _task: Optional[Awaitable[Any]] = None

    async def __call__(self) -> Any:
        async with asyncio.timeout(self.timeout):
            result = self.function(*self.args, **self.kwargs)
            if asyncio.iscoroutine(result):
                self._task = asyncio.create_task(result)
                result = await self._task

        await self.done(result)

        return result

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Task):
            return False

        return self.id == other.id

    def __await__(self):
        return self._result_event.wait().__await__()

    def is_done(self) -> bool:
        return self._result_event.is_set()

    async def done(self, result: _T_DONE) -> _T_DONE:
        if self.is_done():
            raise AlreadyDoneException

        self._result_event.set()
        self.result = result

        return self.result

    def as_dict(self) -> TaskDict:
        return {
            "function": dump_attribute(self.function),
            "args": self.args,
            "kwargs": self.kwargs,
            "route": str(self.route),
            "id": self.id,
        }

    @classmethod
    def from_dict(cls, data: TaskDict) -> "Task":
        func: FunctionType = load_attribute(data["function"])
        try:
            if func.is_wrapped_task:  # type: ignore
                func = func.__wrapped__  # type: ignore
        except AttributeError:
            pass

        return cls(
            function=func,
            args=data["args"],
            kwargs=data["kwargs"],
            route=Route[data["route"]],
            id=data["id"],
        )
