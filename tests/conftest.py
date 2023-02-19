import asyncio
import math
from collections.abc import AsyncGenerator

import pytest

from aiodispatch.brokers.memory import MemoryBroker
from aiodispatch.decorators import task as task_decorator
from aiodispatch.dispatch import Dispatcher
from aiodispatch.serializers.json import JsonSerializer
from aiodispatch.tasks import Task
from aiodispatch.worker import Worker


@pytest.fixture
def json_serializer() -> JsonSerializer:
    return JsonSerializer()


@pytest.fixture()
def memory_broker() -> MemoryBroker:
    return MemoryBroker()


@pytest.fixture
def dispatcher(
    memory_broker: MemoryBroker, json_serializer: JsonSerializer
) -> Dispatcher:
    return Dispatcher(broker=memory_broker, serializer=json_serializer)


@task_decorator()
def dummy() -> None:
    ...


@pytest.fixture
async def worker(dispatcher: Dispatcher) -> AsyncGenerator[Worker, None]:
    worker = Worker(dispatcher)

    asyncio.create_task(worker.start())

    yield worker

    if not worker.is_stopping():
        worker.stop()


async def async_dummy_func() -> str:
    return "async_dummy_func"


@pytest.fixture
def task() -> Task:
    return Task(function=async_dummy_func)


@pytest.fixture()
def infinite_task() -> Task:
    async def sleep_forever() -> None:
        await asyncio.sleep(math.inf)

    return Task(function=sleep_forever)
