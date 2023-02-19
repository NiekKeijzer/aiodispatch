import functools
from collections.abc import Awaitable
from types import FunctionType
from typing import Any, Callable

from .dispatch import dispatcher
from .enums import Route
from .tasks import Task


def task(*, route: Route = Route.TASKS) -> Callable:  # type: ignore
    def decorator(func: FunctionType) -> Callable[..., Awaitable[Any]]:
        func.is_wrapped_task = True  # type: ignore

        @functools.wraps(func)
        async def inner(*args: Any, **kwargs: dict[str, Any]) -> Any:
            func_task = Task(function=func, args=args, kwargs=kwargs, route=route)

            dispatch = dispatcher.get()
            return await dispatch.publish(func_task)

        return inner

    return decorator
