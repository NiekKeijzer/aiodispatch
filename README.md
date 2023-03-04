# AioDispatch

[![Test and Lint](https://github.com/NiekKeijzer/aiodispatch/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/NiekKeijzer/aiodispatch/actions/workflows/test.yml)
![Code Coverage](https://raw.githubusercontent.com/NiekKeijzer/aiodispatch/assets/images/coverage.svg)
[![PyPI version](https://badge.fury.io/py/aiodispatch.svg)](https://badge.fury.io/py/aiodispatch)

AioDispatch is a simple and pluggable async dispatcher framework with batteries included. AioDispatch can be used 
 to offload expensive operations to external workers. For example, you might use the framework to send email, execute 
 big queries or analyse large datasets. 

AioDispatch is designed to work right of out the box, but to remain pluggable. For example a custom broker is 
 a matter of subclassing `aiodispatch.brokers.abc.Broker` and a serializer `aiodispatch.serializers.abc.Serializer`. 

## Install

```bash 
pip install aiodispatch
```

## Usage 

```python
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
```
