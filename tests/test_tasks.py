import asyncio
import uuid

import pytest
from pytest_mock import MockerFixture

from aiodispatch.decorators import task as task_decorator
from aiodispatch.enums import Route
from aiodispatch.exceptions import AlreadyDoneException
from aiodispatch.tasks import Task
from aiodispatch.utils import dump_attribute, generate_uuid


def dummy_func() -> str:
    return "dummy_func"


async def async_dummy_func() -> str:
    return "async_dummy_func"


@pytest.fixture
def task() -> Task:
    return Task(
        function=dummy_func,  # type: ignore
    )


@pytest.fixture
def async_task() -> Task:
    return Task(
        function=async_dummy_func,
    )


async def test_function_call_is_proxied(mocker: MockerFixture, task: Task) -> None:
    patched = mocker.patch.object(asyncio, "iscoroutine")
    patched.return_value = False

    result = await task()
    patched.assert_called_with("dummy_func")

    assert "dummy_func" == result


async def test_function_call_is_proxied_and_awaited(async_task: Task) -> None:
    result = await async_task()

    assert "async_dummy_func" == result


def test_task_dict(task: Task) -> None:
    task_dict = task.as_dict()

    assert "tests.test_tasks:dummy_func" == task_dict["function"]
    assert {} == task_dict["kwargs"]
    assert str(task.route) == task_dict["route"]

    assert isinstance(task_dict["id"], str)
    assert uuid.UUID(task_dict["id"])  # ensure the id is uuid


def test_task_from_dict(task: Task) -> None:
    task_dict = task.as_dict()
    new_task = Task.from_dict(task_dict)

    assert callable(new_task.function)
    assert Route.TASKS == new_task.route


@task_decorator()
def decorated_function() -> None:
    ...


def test_decorated_task_from_dict() -> None:
    task = Task.from_dict(
        {
            "function": dump_attribute(decorated_function),
            "args": tuple([]),
            "kwargs": {},
            "route": str(Route.TASKS),
            "id": generate_uuid(),
        }
    )

    assert decorated_function.__wrapped__ == task.function


def test_task_equality(task: Task) -> None:
    task_dict = task.as_dict()
    new_task = Task.from_dict(task_dict)

    assert task == new_task
    assert task != async_task


def test_task_inequality(task: Task, async_task: Task) -> None:
    assert task != async_task
    assert task != "certainly not a task"


async def test_task_timeout() -> None:
    async def slow() -> None:
        await asyncio.sleep(2)

    task = Task(function=slow, timeout=0)
    with pytest.raises(asyncio.TimeoutError):
        await task()


async def test_task_done(task: Task) -> None:
    result = object()
    assert task.result is None
    assert not task.is_done()
    await task.done(result)

    assert result == task.result


async def test_task_done_once(task: Task) -> None:
    result = object()
    await task.done(result)

    with pytest.raises(AlreadyDoneException):
        await task.done(result)


async def test_task_wait_until_done(task: Task) -> None:
    result = object()

    async def wait_for_task() -> None:
        await task

    async with asyncio.TaskGroup() as tg:
        aiotask = tg.create_task(wait_for_task())
        tg.create_task(task.done(result))

    assert aiotask.done()
    assert task.is_done()
    assert result == task.result


async def test_async_task_done(async_task: Task) -> None:
    assert not async_task.is_done()

    await async_task()
    assert async_task.is_done()


async def test_async_task_timeout() -> None:
    async def slow() -> None:
        await asyncio.sleep(2)

    task = Task(function=slow, timeout=0)
    with pytest.raises(asyncio.TimeoutError):
        await task()
