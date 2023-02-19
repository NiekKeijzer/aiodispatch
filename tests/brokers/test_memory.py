import asyncio

import pytest

from aiodispatch.brokers.memory import MemoryBroker


@pytest.fixture
def broker() -> MemoryBroker:
    return MemoryBroker()


async def test_publish(broker: MemoryBroker) -> None:
    assert 0 == len(broker.queues)
    await broker.publish("test", b"test")

    assert 1 == len(broker.queues)
    assert "test" in broker.queues
    assert 1 == broker.queues["test"].qsize()


async def test_queue_size() -> None:
    broker = MemoryBroker(1)

    await broker.publish("test", b"test")
    with pytest.raises(asyncio.TimeoutError):
        # Should fail because the queue is full and nothing is pulling item
        async with asyncio.timeout(0):
            await broker.publish("test", b"test")


async def test_consume_queue(broker: MemoryBroker) -> None:
    key = "test"
    payload = b"test"
    await broker.publish(key, payload)

    assert 1 == broker.queues[key].qsize()

    channel = broker.subscribe(key)
    assert payload == await anext(channel)

    assert 0 == broker.queues[key].qsize()
