import asyncio

from aiodispatch.brokers.memory import MemoryBroker
from aiodispatch.decorators import task
from aiodispatch.dispatch import Dispatcher
from aiodispatch.serializers.json import JsonSerializer
from aiodispatch.worker import Worker


@task()
async def slow_greeter(name: str) -> None:
    await asyncio.sleep(2)
    print(f"Hello {name}")


async def producer(num: int = 10) -> None:
    for i in range(num):
        await slow_greeter(name=str(i))


async def main():
    broker = MemoryBroker()
    serializer = JsonSerializer()
    dispatcher = Dispatcher(broker, serializer)
    worker = Worker(dispatcher, semaphore=asyncio.Semaphore(1))

    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker.start())
        tg.create_task(producer())


if __name__ == "__main__":
    asyncio.run(main())
